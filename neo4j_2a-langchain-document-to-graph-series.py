# neo4j_document_processor.py
import os
from pathlib import Path
from dotenv import load_dotenv
import warnings
from typing import List, Dict, Any, Optional, Union
import json

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

# Main function to process documents and build graph
def process_document_to_graph(document_path: str, chunk_size: int = 1000, chunk_overlap: int = 100, clear_existing: bool = True):
    """Process document and build Neo4j graph.
    
    Args:
        document_path: Path to the document to process
        chunk_size: Size of chunks to split document into
        chunk_overlap: Overlap between chunks
        clear_existing: Whether to clear existing data in the Neo4j database
    """
    print(f"\n{'='*50}")
    print(f"DOCUMENT TO GRAPH PROCESSING: {os.path.basename(document_path)}")
    print(f"{'='*50}\n")
    
    try:
        # Initialize Neo4j graph
        print("Connecting to Neo4j...")
        graph = init_neo4j_graph()
        print("Connected to Neo4j successfully.")
        
        # Load document
        print(f"Loading document: {document_path}")
        documents = load_document(document_path)
        print(f"✓ Loaded {len(documents)} documents/pages from {document_path}")
        
        # Split documents into manageable chunks
        print(f"Splitting document into chunks (size={chunk_size}, overlap={chunk_overlap})...")
        chunks = split_documents(documents, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        print(f"✓ Split into {len(chunks)} chunks")
        
        # Extract entities and relationships using LLM
        print("\nExtracting entities and relationships...")
        all_extracted_data = []
        for i, chunk in enumerate(chunks):
            print(f"  Processing chunk {i+1}/{len(chunks)}...")
            text = chunk.page_content
            extracted_data = extract_entities_relationships(text)
            
            # Log what was found in this chunk
            entity_count = len(extracted_data.get("entities", []))
            relationship_count = len(extracted_data.get("relationships", []))
            print(f"  ✓ Found {entity_count} entities and {relationship_count} relationships in chunk {i+1}")
            
            if entity_count > 0 or relationship_count > 0:
                all_extracted_data.append(extracted_data)
        
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
    
    args = parser.parse_args()
    
    process_document_to_graph(
        document_path=args.document_path,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        clear_existing=not args.preserve
    )