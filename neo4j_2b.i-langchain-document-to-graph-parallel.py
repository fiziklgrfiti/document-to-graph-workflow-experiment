# neo4j_document_processor.py
import os
from pathlib import Path
from dotenv import load_dotenv
import warnings
from typing import List, Dict, Any, Optional, Union
import json
import concurrent.futures
import time
from tqdm import tqdm  # For progress bars
import pickle  # For saving/loading extracted data
import hashlib  # For generating unique ids for chunks

# LangChain imports
from langchain_community.document_loaders import TextLoader, PyPDFLoader, UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.graphs import Neo4jGraph
from langchain.schema import Document
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables from .env file
load_dotenv()
warnings.filterwarnings("ignore")

# Initialize Neo4j connection
def init_neo4j_graph():
    """Initialize and return a Neo4j graph connection."""
    graph = Neo4jGraph(
        url=("bolt://localhost:7687"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD")
    )
    return graph

# Document Loading
def load_document(document_path: str) -> List[Document]:
    """Load document from various file types and return as LangChain documents.
    
    Note: For markdown files, you need to install the 'markdown' package:
    pip install markdown
    """
    if not os.path.exists(document_path):
        raise FileNotFoundError(f"Document not found: {document_path}")
    
    file_extension = os.path.splitext(document_path)[1].lower()
    
    try:
        if file_extension == '.pdf':
            loader = PyPDFLoader(document_path)
            return loader.load()
        elif file_extension == '.md':
            try:
                loader = UnstructuredMarkdownLoader(document_path)
                return loader.load()
            except ImportError as e:
                print(f"Error loading markdown: {e}. Install markdown package with 'pip install markdown'")
                # Fallback to text loader
                print("Falling back to TextLoader for markdown file...")
                loader = TextLoader(document_path)
                return loader.load()
        elif file_extension in ['.txt', '']:
            loader = TextLoader(document_path)
            return loader.load()
        else:
            print(f"Unsupported file type: {file_extension}. Trying TextLoader...")
            # Try with text loader as a fallback
            loader = TextLoader(document_path)
            return loader.load()
    except Exception as e:
        print(f"Error loading document {document_path}: {e}")
        # Provide sample content for testing when document loading fails
        sample_text = """
            The air in the Green Room hung thick with unspoken tensions. Elias, the veteran leading man, meticulously adjusted his 
            tie, his gaze pointedly avoiding Clara, the young ingenue. They'd had a disastrous rehearsal yesterday – Clara's 
            lines, delivered with a nervous tremor, had earned her a sharp, though expertly veiled, reprimand from Elias.

            Across the room, Liam, the comedic relief, was attempting to lighten the mood, juggling oranges and cracking jokes. 
            Liam and Clara had a playful, flirty dynamic; he seemed genuinely fond of her, and she always responded with a bright 
            smile, though he suspected she was merely being polite. 

            Seraphina, the stage manager, a whirlwind of controlled chaos, was coordinating last-minute cues. Seraphina and Elias 
            had a history, a quiet understanding forged through years of working together – a past relationship they now navigated 
            with professional courtesy.  She shot him a concerned look; she knew he was still feeling guilty about the incident 
            with Clara. 

            Suddenly, Daniel, the brooding antagonist, entered, radiating an intimidating presence. Daniel and Elias had a rivalry 
            both on and off stage, stemming from a shared ambition for the director's approval. Liam, ever the peacemaker, tried 
            to engage Daniel in a lighthearted exchange, but the actor simply grunted in response. Clara, noticing Daniel's mood, 
            subtly offered him a comforting smile, a gesture that seemed to surprise even her.  Seraphina sighed, observing the 
            complex web of relationships, and muttered to herself, "Just ten more minutes until curtain."
            """
        print("Using sample text for testing purposes.")
        return [Document(page_content=sample_text, metadata={"source": document_path})]

# Text Splitting
def split_documents(documents: List[Document], chunk_size: int = 1000, chunk_overlap: int = 100) -> List[Document]:
    """Split documents into manageable chunks for processing."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return text_splitter.split_documents(documents)

# LLM-based extraction
def extract_entities_relationships(text_chunk: str) -> Dict[str, Any]:
    """Use LLM to extract entities, relationships, and properties from text."""
    # Initialize Ollama with your preferred model
    llm = Ollama(model="gemma3:12b", temperature=0.3)
    
    prompt_template = """
    You are a specialized AI trained to extract entities & relationships from documents.
    Analyze the following text and extract:
    
    1. ENTITIES: Identify all significant entities (people, places, things, concepts, etc.)
    2. RELATIONSHIPS: Identify relationships between these entities
    3. PROPERTIES: Extract attributes/properties for each entity
    
    Format your response as valid JSON with this structure:
    {{
      "entities": [
        {{
          "id": "unique_identifier",
          "type": "person/place/organization/etc",
          "name": "entity_name",
          "properties": {{
            "property1": "value1",
            "property2": "value2"
          }}
        }}
      ],
      "relationships": [
        {{
          "source": "source_entity_id",
          "target": "target_entity_id",
          "type": "relationship_type",
          "properties": {{
            "property1": "value1"
          }}
        }}
      ]
    }}
    
    Ensure entity IDs are unique and used consistently for relationships.
    
    Text:
    {text}
    
    Return only valid JSON that can be parsed. Do not include any explanation or commentary outside the JSON structure.
    """
    
    prompt = PromptTemplate.from_template(prompt_template)
    
    # Create chain
    chain = prompt | llm | StrOutputParser()
    
    result_text = ""
    try:
        result_text = chain.invoke({"text": text_chunk})
        
        # Find JSON in the result
        json_start = result_text.find('{')
        json_end = result_text.rfind('}') + 1
        
        if json_start != -1 and json_end != -1:
            json_str = result_text[json_start:json_end]
            try:
                data = json.loads(json_str)
                return data
            except json.JSONDecodeError as je:
                print(f"Error parsing JSON: {je}")
                print("Attempted JSON parsing for: ", json_str[:200] + "..." if len(json_str) > 200 else json_str)
        else:
            print("No valid JSON found in LLM response")
        
        return {"entities": [], "relationships": []}
            
    except Exception as e:
        print(f"Error extracting entities and relationships with LLM: {e}")
        if result_text:
            print("LLM response: ", result_text[:200] + "..." if len(result_text) > 200 else result_text)
        return {"entities": [], "relationships": []}

# Build Neo4j graph
def build_graph(graph: Neo4jGraph, extracted_data: Dict[str, Any], clear_existing: bool = True):
    """Build Neo4j graph from extracted entities and relationships.
    
    Args:
        graph: Neo4j graph connection
        extracted_data: Dictionary with entities and relationships data
        clear_existing: Whether to clear the existing graph data
    """
    # Clear existing graph if requested
    if clear_existing:
        graph.query("MATCH (n) DETACH DELETE n")
    
    # Process entities
    for entity in extracted_data.get("entities", []):
        # Convert properties dict to a format compatible with Neo4j
        properties = {}
        properties["id"] = entity.get("id", "")
        properties["name"] = entity.get("name", "")
        
        # Add all other properties
        for key, value in entity.get("properties", {}).items():
            properties[key] = value
        
        # Create entity node with dynamic type label
        entity_type = entity.get("type", "Entity")
        # Ensure the entity type is valid for Neo4j (no spaces or special chars)
        entity_type = "".join(c if c.isalnum() else "_" for c in entity_type)
        
        query = f"""
        MERGE (e:{entity_type} {{id: $id}})
        SET e += $properties
        """
        
        try:
            graph.query(query, params={
                "id": properties["id"],
                "properties": properties
            })
        except Exception as e:
            print(f"Error creating entity node {properties['id']}: {e}")
    
    # Process relationships
    for rel in extracted_data.get("relationships", []):
        source_id = rel.get("source", "")
        target_id = rel.get("target", "")
        
        # Skip if source or target is missing
        if not source_id or not target_id:
            continue
            
        # Ensure relationship type is valid for Neo4j (uppercase, no spaces)
        rel_type = rel.get("type", "RELATED_TO").upper().replace(" ", "_")
        rel_type = "".join(c if c.isalnum() or c == "_" else "_" for c in rel_type)
        
        # Prepare relationship properties
        rel_properties = rel.get("properties", {})
        
        # Build dynamic query based on relationship properties
        if rel_properties:
            # Convert properties to SET clause
            props_query = "SET r += $rel_properties"
        else:
            props_query = ""
        
        query = f"""
        MATCH (source {{id: $source_id}})
        MATCH (target {{id: $target_id}})
        MERGE (source)-[r:{rel_type}]->(target)
        {props_query}
        """
        
        try:
            graph.query(query, params={
                "source_id": source_id,
                "target_id": target_id,
                "rel_properties": rel_properties
            })
        except Exception as e:
            print(f"Error creating relationship from {source_id} to {target_id}: {e}")

# Function to save extracted data
def save_extracted_data(data_list: List[Dict[str, Any]], output_file: str):
    """Save extracted data to a file.
    
    Args:
        data_list: List of extracted data dictionaries
        output_file: File path to save data to
    """
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    with open(output_file, 'wb') as f:
        pickle.dump(data_list, f)
    print(f"✓ Saved extracted data to {output_file}")

# Function to load extracted data
def load_extracted_data(input_file: str) -> List[Dict[str, Any]]:
    """Load extracted data from a file.
    
    Args:
        input_file: File path to load data from
        
    Returns:
        List of extracted data dictionaries
    """
    if not os.path.exists(input_file):
        print(f"❌ No saved data found at {input_file}")
        return []
        
    with open(input_file, 'rb') as f:
        data_list = pickle.load(f)
    print(f"✓ Loaded extracted data from {input_file} ({len(data_list)} chunks)")
    return data_list

# Get default output file path for extracted data
def get_default_output_file(document_path: str) -> str:
    """Get default output file path for extracted data.
    
    Args:
        document_path: Path to the input document
        
    Returns:
        Default path for extracted data file
    """
    document_basename = os.path.basename(document_path)
    document_name, _ = os.path.splitext(document_basename)
    return os.path.join('extracted_data', f"{document_name}.pkl")

# Merge extracted data to avoid duplicates
def merge_extracted_data(data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge extracted data from multiple chunks, avoiding duplicates."""
    merged_data = {"entities": [], "relationships": []}
    entity_ids = set()
    
    # Merge entities
    for data in data_list:
        for entity in data.get("entities", []):
            if entity.get("id") not in entity_ids:
                merged_data["entities"].append(entity)
                entity_ids.add(entity.get("id"))
    
    # Track processed relationships to avoid duplicates
    processed_relationships = set()
    
    # Merge relationships
    for data in data_list:
        for relationship in data.get("relationships", []):
            source = relationship.get("source")
            target = relationship.get("target")
            rel_type = relationship.get("type")
            
            # Create a unique key for this relationship
            rel_key = f"{source}-{rel_type}-{target}"
            
            if rel_key not in processed_relationships:
                merged_data["relationships"].append(relationship)
                processed_relationships.add(rel_key)
    
    return merged_data

# Function to process a single chunk
def process_chunk(chunk, chunk_index, total_chunks):
    """Process a single document chunk.
    
    Args:
        chunk: Document chunk to process
        chunk_index: Index of this chunk
        total_chunks: Total number of chunks
        
    Returns:
        Extracted data from this chunk
    """
    try:
        text = chunk.page_content
        print(f"  Processing chunk {chunk_index+1}/{total_chunks}...")
        extracted_data = extract_entities_relationships(text)
        
        # Log what was found in this chunk
        entity_count = len(extracted_data.get("entities", []))
        relationship_count = len(extracted_data.get("relationships", []))
        print(f"  ✓ Found {entity_count} entities and {relationship_count} relationships in chunk {chunk_index+1}")
        
        return extracted_data if (entity_count > 0 or relationship_count > 0) else None
    except Exception as e:
        print(f"  ❌ Error processing chunk {chunk_index+1}: {e}")
        return None

# Main function to process documents and build graph
def process_document_to_graph(
    document_path: str, 
    chunk_size: int = 1000, 
    chunk_overlap: int = 100, 
    clear_existing: bool = True,
    parallel: bool = False,
    max_workers: int = 4,
    verbose: bool = True,
    start_chunk: int = 0,
    end_chunk: Optional[int] = None,
    save_data: bool = False,
    load_data: bool = False,
    output_file: Optional[str] = None
):
    """Process document and build Neo4j graph.
    
    Args:
        document_path: Path to the document to process
        chunk_size: Size of chunks to split document into
        chunk_overlap: Overlap between chunks
        clear_existing: Whether to clear existing data in the Neo4j database
        parallel: Whether to process chunks in parallel
        max_workers: Maximum number of worker threads for parallel processing
        verbose: Whether to print detailed progress information
        start_chunk: Index of first chunk to process (0-based)
        end_chunk: Index of last chunk to process (None means process all)
        save_data: Whether to save extracted data to file
        load_data: Whether to load previously extracted data from file
        output_file: Path to save/load extracted data (default: based on document name)
    """
    print(f"\n{'='*50}")
    print(f"DOCUMENT TO GRAPH PROCESSING: {os.path.basename(document_path)}")
    print(f"{'='*50}\n")
    
    try:
        # Initialize Neo4j graph
        print("Connecting to Neo4j...")
        graph = init_neo4j_graph()
        print("Connected to Neo4j successfully.")
        
        # Get default output file if not specified
        if output_file is None:
            output_file = get_default_output_file(document_path)
        
        all_extracted_data = []
        
        # Check if we should load from file
        if load_data:
            all_extracted_data = load_extracted_data(output_file)
            if all_extracted_data:
                print("Using loaded data instead of processing document.")
        
        # If no data loaded or load_data is False, process the document
        if not all_extracted_data:
            # Load document
            print(f"Loading document: {document_path}")
            documents = load_document(document_path)
            print(f"✓ Loaded {len(documents)} documents/pages from {document_path}")
            
            # Split documents into manageable chunks
            print(f"Splitting document into chunks (size={chunk_size}, overlap={chunk_overlap})...")
            chunks = split_documents(documents, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            print(f"✓ Split into {len(chunks)} chunks")
            
            # Select subset of chunks if specified
            if end_chunk is None:
                end_chunk = len(chunks)
            else:
                end_chunk = min(end_chunk, len(chunks))
                
            chunks = chunks[start_chunk:end_chunk]
            print(f"Selected {len(chunks)} chunks for processing (from index {start_chunk} to {end_chunk-1})")
            
            # Extract entities and relationships using LLM
            print("\nExtracting entities and relationships...")
            
            # For parallel processing
            if parallel:
                print(f"Using parallel processing with {max_workers} workers")
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                    # Submit all chunk processing tasks
                    future_to_chunk = {
                        executor.submit(process_chunk, chunk, i, len(chunks)): i 
                        for i, chunk in enumerate(chunks)
                    }
                    
                    # Process completed tasks
                    for future in concurrent.futures.as_completed(future_to_chunk):
                        extracted_data = future.result()
                        if extracted_data:
                            all_extracted_data.append(extracted_data)
            # For sequential processing
            else:
                print("Using sequential processing")
                for i, chunk in enumerate(chunks):
                    extracted_data = process_chunk(chunk, i, len(chunks))
                    if extracted_data:
                        all_extracted_data.append(extracted_data)
            
            # Save extracted data if requested
            if save_data and all_extracted_data:
                save_extracted_data(all_extracted_data, output_file)
        
        if not all_extracted_data:
            print("\n⚠️ Warning: No entities or relationships were extracted from the document.")
            return
        
        # Merge data from all chunks
        print("\nMerging data from all chunks...")
        merged_data = merge_extracted_data(all_extracted_data)
        
        print(f"✓ Total extracted: {len(merged_data['entities'])} unique entities and {len(merged_data['relationships'])} unique relationships")
        
        # Preview some of the extracted entities
        if merged_data['entities']:
            print("\nSample entities extracted:")
            for entity in merged_data['entities'][:min(3, len(merged_data['entities']))]:
                entity_type = entity.get("type", "Unknown")
                entity_name = entity.get("name", entity.get("id", "Unnamed"))
                print(f"  - {entity_type}: {entity_name}")
                # Show some properties if available
                properties = entity.get("properties", {})
                if properties:
                    prop_sample = list(properties.items())[:min(2, len(properties))]
                    props_str = ", ".join([f"{k}: {v}" for k, v in prop_sample])
                    if len(properties) > 2:
                        props_str += ", ..."
                    print(f"    Properties: {props_str}")
            
            if len(merged_data['entities']) > 3:
                print(f"    ... and {len(merged_data['entities']) - 3} more entities")
        
        # Preview some relationships
        if merged_data['relationships']:
            print("\nSample relationships extracted:")
            for rel in merged_data['relationships'][:min(3, len(merged_data['relationships']))]:
                source = rel.get("source", "Unknown")
                target = rel.get("target", "Unknown")
                rel_type = rel.get("type", "Unknown")
                print(f"  - {source} → {rel_type} → {target}")
            
            if len(merged_data['relationships']) > 3:
                print(f"    ... and {len(merged_data['relationships']) - 3} more relationships")
        
        # Build graph
        print("\nBuilding Neo4j graph...")
        if clear_existing:
            print("  Warning: Clearing existing data in Neo4j database")
        build_graph(graph, merged_data, clear_existing=clear_existing)
        print("✓ Graph built successfully")
        
        # Verify data was loaded
        print("\nVerifying data in Neo4j...")
        entity_query = """
        MATCH (n)
        RETURN DISTINCT labels(n) AS type, count(n) AS count
        ORDER BY count DESC
        """
        entity_result = graph.query(entity_query)
        
        print("\nEntities in the graph:")
        for item in entity_result:
            print(f"  {item['type']}: {item['count']} nodes")
        
        relationship_query = """
        MATCH ()-[r]->()
        RETURN DISTINCT type(r) AS type, count(r) AS count
        ORDER BY count DESC
        """
        relationship_result = graph.query(relationship_query)
        
        print("\nRelationships in the graph:")
        for item in relationship_result:
            print(f"  {item['type']}: {item['count']} relationships")
        
        print(f"\n{'='*50}")
        print("PROCESSING COMPLETE")
        print(f"{'='*50}")
        
    except Exception as e:
        print(f"\n❌ Error during document processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Process documents and build a Neo4j knowledge graph")
    parser.add_argument("document_path", help="Path to the document to process")
    parser.add_argument("--chunk-size", type=int, default=1000, help="Size of chunks to split document into")
    parser.add_argument("--chunk-overlap", type=int, default=100, help="Overlap between chunks")
    parser.add_argument("--preserve", action="store_true", help="Preserve existing data in Neo4j (don't clear)")
    parser.add_argument("--parallel", action="store_true", help="Process chunks in parallel")
    parser.add_argument("--workers", type=int, default=4, help="Number of worker threads for parallel processing")
    parser.add_argument("--quiet", action="store_true", help="Reduce verbosity of output")
    parser.add_argument("--start-chunk", type=int, default=0, help="Start processing from this chunk index")
    parser.add_argument("--end-chunk", type=int, default=None, help="Stop processing at this chunk index")
    parser.add_argument("--save", action="store_true", help="Save extracted data to file for later use")
    parser.add_argument("--load", action="store_true", help="Load previously extracted data instead of processing again")
    parser.add_argument("--output-file", help="Path to save/load extracted data (default: based on document name)")
    
    args = parser.parse_args()
    
    # Process only a subset of chunks if specified
    if args.start_chunk > 0 or args.end_chunk is not None:
        print(f"Processing chunks from {args.start_chunk} to {args.end_chunk if args.end_chunk else 'end'}")
    
    # Install required packages if not already installed
    try:
        import tqdm
    except ImportError:
        print("Installing tqdm for progress bars...")
        import subprocess
        subprocess.check_call(["pip", "install", "tqdm"])
        import tqdm
    
    start_time = time.time()
    
    process_document_to_graph(
        document_path=args.document_path,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        clear_existing=not args.preserve,
        parallel=args.parallel,
        max_workers=args.workers,
        verbose=not args.quiet,
        start_chunk=args.start_chunk,
        end_chunk=args.end_chunk,
        save_data=args.save,
        load_data=args.load,
        output_file=args.output_file
    )
    
    total_time = time.time() - start_time
    print(f"\nTotal processing time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")