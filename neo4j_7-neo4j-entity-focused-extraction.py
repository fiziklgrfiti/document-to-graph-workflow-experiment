# neo4j_entity_focused_extraction.py
import os
import argparse
from dotenv import load_dotenv
import warnings
from typing import List, Dict, Any, Optional, Tuple
import time
import json
import pickle
from pathlib import Path

# LangChain imports
from langchain_community.graphs import Neo4jGraph
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load environment variables from .env file
load_dotenv()
warnings.filterwarnings("ignore")

# Global verbose flag
VERBOSE = False

def initialize_neo4j_connection() -> Neo4jGraph:
    """Initialize and return a Neo4j graph connection."""
    try:
        graph = Neo4jGraph(
            url=("bolt://localhost:7687"),
            username=os.getenv("NEO4J_USERNAME"),
            password=os.getenv("NEO4J_PASSWORD")
        )
        # Test connection
        graph.query("RETURN 1 as test")
        print("✓ Successfully connected to Neo4j")
        return graph
    except Exception as e:
        print(f"❌ Failed to connect to Neo4j: {e}")
        print("  Please check your credentials and database availability.")
        raise e

def initialize_llm(model_name: str = "llama3.1:latest", temperature: float = 0.1) -> Ollama:
    """Initialize and return the LLM."""
    # List of models to try in order of preference
    models_to_try = [
        model_name,        # Try the specified model first
        "gemma3:12b",      # Good general model
        "gemma3:4b",       # Alternative
        "mistral:7b"       # Fallback option
    ]
    
    base_url = "http://localhost:11434"
    
    # Remove duplicates while preserving order
    unique_models = []
    for model in models_to_try:
        if model not in unique_models:
            unique_models.append(model)
    
    # Try each model in sequence
    last_exception = None
    for model in unique_models:
        try:
            print(f"Attempting to use LLM model: {model}")
            llm = Ollama(
                model=model,
                temperature=temperature,
                base_url=base_url
            )
            
            # Test the LLM with a simple query
            test_response = llm.invoke("Hello")
            print(f"✓ Successfully connected to Ollama using model: {model}")
            return llm
        except Exception as e:
            print(f"❌ Failed to use model {model}: {e}")
            last_exception = e
    
    # If we get here, all models failed
    raise ValueError(f"All LLM models failed. Last error: {last_exception}")

def get_entity_types(graph: Neo4jGraph) -> List[str]:
    """Get all entity types (node labels) from the Neo4j graph."""
    try:
        # Query to get all labels in the graph
        result = graph.query("CALL db.labels() YIELD label RETURN label")
        labels = [record["label"] for record in result]
        
        # Filter out system labels or labels you want to exclude
        excluded_labels = ["Document", "Chunk", "Source", "File"]
        entity_types = [label for label in labels if label not in excluded_labels]
        
        return entity_types
    except Exception as e:
        print(f"❌ Error getting entity types: {e}")
        return []

def get_entities_by_type(graph: Neo4jGraph, entity_type: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Get entities of a specific type from the graph."""
    try:
        # Query to get entities of the specified type with their properties
        query = f"""
        MATCH (e:{entity_type})
        RETURN e.id as id, e.name as name, e.description as description, 
               e.text as text, e.type as type, e
        LIMIT {limit}
        """
        
        result = graph.query(query)
        
        # Process the results to get a simpler format
        entities = []
        for record in result:
            # Extract node properties
            node_props = record["e"]
            
            # Create entity record with common fields
            entity = {
                "id": record["id"],
                "name": record["name"],
                "type": entity_type,
                "description": record["description"] if record["description"] else None,
                "attributes": {}
            }
            
            # Add all other properties as attributes
            for key, value in node_props.items():
                if key not in ["id", "name", "type", "description"] and value is not None:
                    entity["attributes"][key] = value
            
            entities.append(entity)
        
        return entities
    except Exception as e:
        print(f"❌ Error getting entities of type {entity_type}: {e}")
        return []

def get_related_documents(
    graph: Neo4jGraph, 
    entity_id: str,
    distance: int = 2
) -> List[Dict[str, Any]]:
    """
    Find documents or text chunks in the graph related to the entity of interest.
    
    Args:
        graph: Neo4j graph connection
        entity_id: ID of the entity of interest
        distance: Max path length to consider for relationships
    
    Returns:
        List of document chunks related to the entity
    """
    try:
        # Query to find related document nodes or chunks
        # This assumes a specific graph structure - adjust as needed for your graph
        query = f"""
        MATCH (e {{id: $entity_id}})
        OPTIONAL MATCH path = (e)-[*1..{distance}]-(d)
        WHERE d.text IS NOT NULL AND d.text <> ""
        WITH d, e, [rel in relationships(path) | type(rel)] AS rel_types
        RETURN d.id as id, d.text as text, 
               labels(d) as labels, d.name as name,
               e.id as entity_id, e.name as entity_name,
               rel_types
        """
        
        result = graph.query(query, params={"entity_id": entity_id})
        
        # Process the results
        document_chunks = []
        for record in result:
            # Skip records without text
            if not record["text"]:
                continue
                
            document_chunks.append({
                "id": record["id"],
                "text": record["text"],
                "labels": record["labels"],
                "name": record["name"],
                "entity_id": record["entity_id"],
                "entity_name": record["entity_name"],
                "relationship_types": record["rel_types"]
            })
        
        # If no document chunks were found directly, try a broader search
        if not document_chunks:
            print("No directly related document chunks found. Trying keyword search...")
            
            # Get the entity name first
            entity_query = """
            MATCH (e {id: $entity_id})
            RETURN e.name as name
            """
            entity_result = graph.query(entity_query, params={"entity_id": entity_id})
            entity_name = entity_result[0]["name"] if entity_result else None
            
            if entity_name:
                # Find document chunks containing the entity name
                keyword_query = """
                MATCH (d)
                WHERE d.text IS NOT NULL AND d.text CONTAINS $keyword
                RETURN d.id as id, d.text as text, 
                       labels(d) as labels, d.name as name,
                       $entity_id as entity_id, $entity_name as entity_name,
                       [] as rel_types
                LIMIT 20
                """
                
                keyword_result = graph.query(
                    keyword_query, 
                    params={"keyword": entity_name, "entity_id": entity_id, "entity_name": entity_name}
                )
                
                # Process the results
                for record in keyword_result:
                    if not record["text"]:
                        continue
                        
                    document_chunks.append({
                        "id": record["id"],
                        "text": record["text"],
                        "labels": record["labels"],
                        "name": record["name"],
                        "entity_id": record["entity_id"],
                        "entity_name": record["entity_name"],
                        "relationship_types": record["rel_types"],
                        "match_type": "keyword"
                    })
        
        return document_chunks
    except Exception as e:
        print(f"❌ Error getting related documents: {e}")
        return []

def load_document(document_path: str) -> List[Document]:
    """Load document from file and return as LangChain documents."""
    try:
        # Simple text loader
        with open(document_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Create a Document object
        doc = Document(page_content=text, metadata={"source": document_path})
        return [doc]
    except Exception as e:
        print(f"❌ Error loading document {document_path}: {e}")
        return []

def split_document(document: Document, chunk_size: int = 1000, chunk_overlap: int = 100) -> List[Document]:
    """Split document into manageable chunks for processing."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return text_splitter.split_documents([document])

def find_entity_in_document(
    document_path: str,
    entity_name: str,
    entity_type: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[Document]:
    """
    Find chunks in a document that mention the entity of interest.
    
    Args:
        document_path: Path to the document
        entity_name: Name of the entity to look for
        entity_type: Type/category of the entity
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
    
    Returns:
        List of document chunks that mention the entity
    """
    # Load document
    documents = load_document(document_path)
    if not documents:
        return []
    
    # Split the document
    chunks = split_document(documents[0], chunk_size, chunk_overlap)
    print(f"Split document into {len(chunks)} chunks")
    
    # Find chunks mentioning the entity
    entity_chunks = []
    for i, chunk in enumerate(chunks):
        # Simple check if the entity name appears in the chunk
        if entity_name.lower() in chunk.page_content.lower():
            # Add metadata for identification
            chunk.metadata["chunk_index"] = i
            chunk.metadata["entity_name"] = entity_name
            chunk.metadata["entity_type"] = entity_type
            entity_chunks.append(chunk)
    
    print(f"Found {len(entity_chunks)} chunks mentioning '{entity_name}'")
    return entity_chunks

def extract_focused_entity_info(
    text: str, 
    entity_name: str, 
    entity_type: str,
    llm: Ollama
) -> Dict[str, Any]:
    """
    Extract focused information about the entity from text.
    
    Args:
        text: Text to analyze
        entity_name: Name of the entity to focus on
        entity_type: Type/category of the entity
        llm: Language model for extraction
    
    Returns:
        Dictionary with extracted entity information
    """
    # Create a focused extraction prompt
    prompt_template = """
    You are a specialized graph entity analysis AI focused on extracting detailed information about a specific entity.

    -Goal-
    Efficiently acquire comprehensive information about a specific entity.
    
    
    ENTITY TO FOCUS ON:
    Name: {entity_name}
    Type: {entity_type}

    YOUR TASK:
    Extract comprehensive information ONLY about this specific entity from the provided text.
    Be thorough and detailed, extracting all properties, attributes, relationships, and contextual information.
    If attributes for the entity are not mentioned in the text, do not make assumptions.
    
    TEXT TO ANALYZE:
    {text}

    INSTRUCTIONS:
    1. Focus EXCLUSIVELY on the specified entity: {entity_name}
    2. If the entity is not meaningfully discussed in the text, then simply return:
    
    {{ "entity_id": "{entity_name}_id", "name": "{entity_name}", "type": "{entity_type}", "confidence": 0.0, "not_found": true }}
    
    3. If the entity is meaningfully discussed in the text, then extract and organize the following information:
       - All attributes, properties, and characteristics of the entity
       - Key relationships with other entities
       - Actions, roles, or behaviors of the entity
       - Contextual information that helps understand the entity better
    4. Organize the information in a structured JSON format as follows:
    
    {{
      "entity_id": "unique_id_for_entity",
      "name": "{entity_name}",
      "type": "{entity_type}",
      "description": "comprehensive description of the entity based on the text",
      "properties": {{
        "property1": "value1",
        "property2": "value2",
        ...
      }},
      "relationships": [
        {{
          "target_entity": "name of related entity",
          "relationship_type": "description of relationship",
          "details": "additional context about this relationship"
        }},
        ...
      ],
      "confidence": 0.X  // Your confidence in the extraction quality (0.0-1.0)
    }}
    
    5. Provide ONLY the valid JSON as your response, with no additional text.
    
    
    Return ONLY valid, parseable JSON.
    """
    
    prompt = PromptTemplate.from_template(prompt_template)
    
    # Create LLM chain
    extraction_chain = prompt | llm | StrOutputParser()
    
    # Invoke the chain
    try:
        try:
            # Add timeout to prevent hanging
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(extraction_chain.invoke, {
                    "entity_name": entity_name,
                    "entity_type": entity_type,
                    "text": text
                })
                result_text = future.result(timeout=900)  # 15-minute timeout
        except concurrent.futures.TimeoutError:
            print(f"❌ Extraction timed out after 900 seconds")
            return {
                "entity_id": f"{entity_name.lower().replace(' ', '_')}_id",
                "name": entity_name,
                "type": entity_type,
                "error": "Extraction timed out"
            }
        
        # Find and parse JSON
        json_start = result_text.find('{')
        json_end = result_text.rfind('}') + 1
        
        if json_start != -1 and json_end != -1:
            json_str = result_text[json_start:json_end]
            try:
                # Parse the extracted JSON
                entity_data = json.loads(json_str)
                
                # Ensure we have the minimum required fields
                if "name" not in entity_data:
                    entity_data["name"] = entity_name
                if "type" not in entity_data:
                    entity_data["type"] = entity_type
                if "entity_id" not in entity_data:
                    entity_data["entity_id"] = f"{entity_name.lower().replace(' ', '_')}_id"
                
                return entity_data
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing JSON response: {e}")
                print("Response was:", json_str)
                # Return basic entity info
                return {
                    "entity_id": f"{entity_name.lower().replace(' ', '_')}_id",
                    "name": entity_name,
                    "type": entity_type,
                    "error": f"JSON parsing error: {e}",
                    "raw_response": result_text
                }
        else:
            print("❌ No valid JSON found in LLM response")
            return {
                "entity_id": f"{entity_name.lower().replace(' ', '_')}_id",
                "name": entity_name,
                "type": entity_type,
                "error": "No JSON found in response",
                "raw_response": result_text
            }
    except Exception as e:
        print(f"❌ Error during entity extraction: {e}")
        return {
            "entity_id": f"{entity_name.lower().replace(' ', '_')}_id",
            "name": entity_name,
            "type": entity_type,
            "error": f"Extraction error: {e}"
        }

def update_entity_in_graph(graph: Neo4jGraph, entity_data: Dict[str, Any], entity_id: str = None) -> str:
    """
    Update or create an entity in the Neo4j graph with enhanced information.
    
    Args:
        graph: Neo4j graph connection
        entity_data: Dictionary with entity information
        entity_id: Original entity ID if this is an update
    
    Returns:
        The ID of the updated or created entity
    """
    # Extract basic entity information
    name = entity_data.get("name", "Unknown")
    entity_type = entity_data.get("type", "Entity")
    description = entity_data.get("description", "")
    
    # Get or create entity ID
    if entity_id:
        # Use provided ID for updates
        target_id = entity_id
    else:
        # Use ID from data or generate one
        target_id = entity_data.get("entity_id", f"{name.lower().replace(' ', '_')}_id")
    
    # Extract properties, handling potential missing fields
    properties = entity_data.get("properties", {})
    
    # Create a dictionary for entity properties
    entity_properties = {
        "id": target_id,
        "name": name,
        "description": description
    }
    
    # Add all other properties
    for key, value in properties.items():
        if key not in ["id", "name", "description"] and value is not None:
            entity_properties[key] = value
    
    # Ensure the entity type is valid for Neo4j (no spaces or special chars)
    entity_type = "".join(c if c.isalnum() else "_" for c in entity_type)
    
    try:
        # Update or create entity node
        query = f"""
        MERGE (e:{entity_type} {{id: $id}})
        SET e += $properties
        RETURN e.id as id
        """
        
        result = graph.query(query, params={
            "id": target_id,
            "properties": entity_properties
        })
        
        entity_id = result[0]["id"] if result else target_id
        
        # Process relationships if available
        relationships = entity_data.get("relationships", [])
        for rel in relationships:
            # Extract relationship information
            target_name = rel.get("target_entity", "").strip()
            rel_type = rel.get("relationship_type", "RELATED_TO").upper().replace(" ", "_")
            
            # Skip if target entity name is missing
            if not target_name:
                continue
                
            # Ensure relationship type is valid for Neo4j (uppercase, no spaces)
            rel_type = "".join(c if c.isalnum() or c == "_" else "_" for c in rel_type)
            
            # Generate a target entity ID
            target_id = f"{target_name.lower().replace(' ', '_')}_id"
            
            # Create or merge the target entity
            target_query = f"""
            MERGE (target:Entity {{id: $target_id}})
            ON CREATE SET target.name = $target_name
            """
            
            graph.query(target_query, params={
                "target_id": target_id,
                "target_name": target_name
            })
            
            # Create the relationship
            rel_query = f"""
            MATCH (source {{id: $source_id}})
            MATCH (target {{id: $target_id}})
            MERGE (source)-[r:{rel_type}]->(target)
            """
            
            # Add relationship properties if available
            rel_properties = {}
            details = rel.get("details")
            if details:
                rel_properties["details"] = details
            
            # Add properties to query if available
            if rel_properties:
                rel_query += "\nSET r += $rel_properties"
                
            graph.query(rel_query, params={
                "source_id": entity_id,
                "target_id": target_id,
                "rel_properties": rel_properties
            })
        
        print(f"✓ Successfully updated entity {name} in Neo4j")
        return entity_id
    except Exception as e:
        print(f"❌ Error updating entity in graph: {e}")
        return target_id

def process_entity_from_documents(
    graph: Neo4jGraph, 
    llm: Ollama,
    entity_id: str,
    document_chunks: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Process an entity from multiple document chunks to create an enhanced entity profile.
    
    Args:
        graph: Neo4j graph connection
        llm: Language model
        entity_id: ID of the entity to enhance
        document_chunks: List of document chunks related to the entity
    
    Returns:
        Dictionary with consolidated entity information
    """
    if not document_chunks:
        print("No document chunks provided for processing")
        return {}
    
    # Get entity information from the graph
    entity_query = """
    MATCH (e {id: $entity_id})
    RETURN e.id as id, e.name as name, e.description as description, 
           e.type as type, labels(e) as labels
    """
    
    entity_result = graph.query(entity_query, params={"entity_id": entity_id})
    
    if not entity_result:
        print(f"❌ Entity with ID {entity_id} not found in the graph")
        return {}
    
    entity_record = entity_result[0]
    entity_name = entity_record["name"]
    entity_type = entity_record["type"] or entity_record["labels"][0]
    
    print(f"\nEnhancing entity: {entity_name} (Type: {entity_type})")
    
    # Process each document chunk
    chunk_results = []
    for i, chunk in enumerate(document_chunks):
        print(f"\nProcessing chunk {i+1}/{len(document_chunks)}")
        
        # Extract focused information about the entity
        extraction_result = extract_focused_entity_info(
            text=chunk["text"],
            entity_name=entity_name,
            entity_type=entity_type,
            llm=llm
        )
        
        # Skip if extraction failed or entity not found in this chunk
        if extraction_result.get("error") or extraction_result.get("not_found"):
            print(f"  Skipping chunk {i+1} - Entity not found or extraction error")
            continue
        
        # Add to results
        chunk_results.append(extraction_result)
        
        # Print some info about what was found
        properties_count = len(extraction_result.get("properties", {}))
        relationships_count = len(extraction_result.get("relationships", []))
        print(f"  Found {properties_count} properties and {relationships_count} relationships")
    
    # Merge results from all chunks
    if not chunk_results:
        print("No successful extractions from any chunks")
        return {}
    
    # Start with the first result as base
    consolidated = chunk_results[0]
    
    # Track property and relationship counts for merging
    all_properties = {}
    all_relationships = {}
    
    # Process each extraction result
    for result in chunk_results:
        # Merge properties
        for prop, value in result.get("properties", {}).items():
            all_properties[prop] = all_properties.get(prop, []) + [value]
        
        # Track relationships by target entity
        for rel in result.get("relationships", []):
            target = rel.get("target_entity", "").strip()
            if not target:
                continue
                
            rel_type = rel.get("relationship_type", "").strip()
            key = f"{target}|{rel_type}"
            
            if key not in all_relationships:
                all_relationships[key] = rel
            else:
                # If we have this relationship already, merge details
                existing_details = all_relationships[key].get("details", "")
                new_details = rel.get("details", "")
                
                if new_details and new_details not in existing_details:
                    if existing_details:
                        all_relationships[key]["details"] = f"{existing_details}; {new_details}"
                    else:
                        all_relationships[key]["details"] = new_details
    
    # Consolidate properties by selecting the most common value for each
    consolidated_properties = {}
    for prop, values in all_properties.items():
        # Count frequency of each value
        value_counts = {}
        for val in values:
            if val is not None:
                # Convert unhashable types (like lists) to strings for counting
                if isinstance(val, (list, dict)):
                    val_key = str(val)
                else:
                    val_key = val
                    
                value_counts[val_key] = value_counts.get(val_key, 0) + 1
        
        # Select the most common value
        if value_counts:
            most_common_key = max(value_counts.items(), key=lambda x: x[1])[0]
            
            # If the most common key is a string representation of a list/dict, 
            # find the original value from values list
            if isinstance(most_common_key, str) and (most_common_key.startswith('[') or most_common_key.startswith('{')):
                for val in values:
                    if str(val) == most_common_key:
                        consolidated_properties[prop] = val
                        break
            else:
                # Use the key directly if it's not a string representation
                consolidated_properties[prop] = most_common_key
        
    # Create consolidated entity data
    consolidated_entity = {
        "entity_id": entity_id,
        "name": entity_name,
        "type": entity_type,
        "description": consolidated.get("description", ""),
        "properties": consolidated_properties,
        "relationships": list(all_relationships.values())
    }
    
    print("\n✓ Successfully consolidated entity information from all chunks")
    print(f"  Final entity has {len(consolidated_properties)} properties and {len(all_relationships)} relationships")
    
    return consolidated_entity

def process_entity_from_file(
    graph: Neo4jGraph,
    llm: Ollama,
    entity_id: str,
    document_path: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> Dict[str, Any]:
    """
    Process an entity from a source document file.
    
    Args:
        graph: Neo4j graph connection
        llm: Language model
        entity_id: ID of the entity to enhance
        document_path: Path to the document
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
    
    Returns:
        Dictionary with consolidated entity information
    """
    # Get entity information from the graph
    entity_query = """
    MATCH (e {id: $entity_id})
    RETURN e.id as id, e.name as name, e.description as description, 
           e.type as type, labels(e) as labels
    """
    
    entity_result = graph.query(entity_query, params={"entity_id": entity_id})
    
    if not entity_result:
        print(f"❌ Entity with ID {entity_id} not found in the graph")
        return {}
    
    entity_record = entity_result[0]
    entity_name = entity_record["name"]
    entity_type = entity_record["type"] or entity_record["labels"][0]
    
    print(f"\nProcessing entity {entity_name} from file {document_path}")
    
    # Find relevant chunks in the document
    entity_chunks = find_entity_in_document(
        document_path=document_path,
        entity_name=entity_name,
        entity_type=entity_type,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    if not entity_chunks:
        print(f"❌ No chunks mentioning '{entity_name}' found in the document")
        return {}
    
    # Convert to format expected by process_entity_from_documents
    document_chunks = []
    for chunk in entity_chunks:
        document_chunks.append({
            "id": f"chunk_{chunk.metadata.get('chunk_index')}",
            "text": chunk.page_content,
            "labels": ["Chunk"],
            "name": f"Chunk {chunk.metadata.get('chunk_index')}",
            "entity_id": entity_id,
            "entity_name": entity_name
        })
    
    # Process the chunks
    return process_entity_from_documents(graph, llm, entity_id, document_chunks)

def save_extraction_results(
    entity_data: Dict[str, Any], 
    output_dir: str = "extracted_entities"
):
    """Save entity extraction results to file."""
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate output filename based on entity ID or name
    entity_id = entity_data.get("entity_id", "").strip()
    entity_name = entity_data.get("name", "unknown_entity").strip()
    
    if not entity_id:
        entity_id = entity_name.lower().replace(" ", "_")
    
    filename = f"{entity_id}_{int(time.time())}.json"
    output_path = os.path.join(output_dir, filename)
    
    # Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(entity_data, f, indent=2)
    
    print(f"✓ Saved extraction results to {output_path}")
    return output_path

def list_available_documents(documents_dir: str = "documents") -> List[str]:
    """List available document files in the documents directory."""
    # Create the directory if it doesn't exist
    Path(documents_dir).mkdir(parents=True, exist_ok=True)
    
    # Find document files
    document_files = []
    for ext in ["*.txt", "*.pdf", "*.md"]:
        document_files.extend(list(Path(documents_dir).glob(ext)))
    
    return [str(path) for path in sorted(document_files)]

def main():
    parser = argparse.ArgumentParser(description="Entity-focused extraction from documents")
    
    # Operational modes
    parser.add_argument("--list-entities", action="store_true", help="List entities in the graph")
    parser.add_argument("--entity-type", help="Filter entities by type")
    parser.add_argument("--entity-id", help="ID of the entity to process")
    parser.add_argument("--document", help="Path to document file to process")
    
    # Processing options
    parser.add_argument("--model", default="llama3.1:latest", help="LLM model name")
    parser.add_argument("--temperature", type=float, default=0.1, help="LLM temperature")
    parser.add_argument("--chunk-size", type=int, default=1000, help="Document chunk size")
    parser.add_argument("--chunk-overlap", type=int, default=200, help="Document chunk overlap")
    parser.add_argument("--output-dir", default="extracted_entities", help="Output directory for extraction results")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Set up global verbosity
    global VERBOSE
    VERBOSE = args.verbose
    
    # Initialize Neo4j connection
    try:
        graph = initialize_neo4j_connection()
    except Exception as e:
        print(f"\nCould not connect to Neo4j: {e}")
        print("Please ensure Neo4j is running and credentials are correct.")
        return
    
    # List entities if requested
    if args.list_entities:
        if args.entity_type:
            # List entities of a specific type
            entities = get_entities_by_type(graph, args.entity_type)
            print(f"\nEntities of type '{args.entity_type}' in the graph:")
            for i, entity in enumerate(entities):
                print(f"{i+1}. {entity['name']} (ID: {entity['id']})")
                if entity.get('description'):
                    print(f"   Description: {entity['description'][:100]}...")
        else:
            # List entity types
            entity_types = get_entity_types(graph)
            print("\nAvailable entity types in the graph:")
            for i, entity_type in enumerate(entity_types):
                count_query = f"MATCH (e:{entity_type}) RETURN count(e) as count"
                count = graph.query(count_query)[0]["count"]
                print(f"{i+1}. {entity_type} ({count} entities)")
            
            # Prompt for entity type selection
            if entity_types and input("\nDo you want to see entities of a specific type? (y/n): ").lower() == 'y':
                selection = input(f"Enter type number (1-{len(entity_types)}): ")
                try:
                    index = int(selection) - 1
                    if 0 <= index < len(entity_types):
                        selected_type = entity_types[index]
                        entities = get_entities_by_type(graph, selected_type)
                        print(f"\nEntities of type '{selected_type}':")
                        for i, entity in enumerate(entities):
                            print(f"{i+1}. {entity['name']} (ID: {entity['id']})")
                            if entity.get('description'):
                                print(f"   Description: {entity['description'][:100]}...")
                except ValueError:
                    print("Invalid selection")
        return
    
    # Interactive mode
    if args.interactive:
        print("\n" + "="*60)
        print("ENTITY-FOCUSED EXTRACTION")
        print("="*60)
        
        # Initialize LLM
        try:
            llm = initialize_llm(model_name=args.model, temperature=args.temperature)
        except Exception as e:
            print(f"\nCould not initialize LLM: {e}")
            print("Please ensure Ollama is running and the model is available.")
            return
        
        # Step 1: Select entity type
        entity_types = get_entity_types(graph)
        print("\nAvailable entity types:")
        for i, entity_type in enumerate(entity_types):
            count_query = f"MATCH (e:{entity_type}) RETURN count(e) as count"
            count = graph.query(count_query)[0]["count"]
            print(f"{i+1}. {entity_type} ({count} entities)")
        
        if not entity_types:
            print("No entity types found in the graph.")
            return
        
        # Get entity type selection
        selected_type_index = -1
        while selected_type_index < 0 or selected_type_index >= len(entity_types):
            try:
                selection = input(f"\nSelect an entity type (1-{len(entity_types)}): ")
                selected_type_index = int(selection) - 1
                if selected_type_index < 0 or selected_type_index >= len(entity_types):
                    print(f"Please enter a number between 1 and {len(entity_types)}")
            except ValueError:
                print("Please enter a valid number")
        
        selected_type = entity_types[selected_type_index]
        
        # Step 2: Select entity
        entities = get_entities_by_type(graph, selected_type)
        if not entities:
            print(f"No entities found of type '{selected_type}'")
            return
        
        print(f"\nEntities of type '{selected_type}':")
        for i, entity in enumerate(entities):
            name = entity.get('name', 'Unnamed')
            entity_id = entity.get('id', 'No ID')
            print(f"{i+1}. {name} (ID: {entity_id})")
            if entity.get('description'):
                print(f"   Description: {entity['description'][:100]}...")
        
        # Get entity selection
        selected_entity_index = -1
        while selected_entity_index < 0 or selected_entity_index >= len(entities):
            try:
                selection = input(f"\nSelect an entity (1-{len(entities)}): ")
                selected_entity_index = int(selection) - 1
                if selected_entity_index < 0 or selected_entity_index >= len(entities):
                    print(f"Please enter a number between 1 and {len(entities)}")
            except ValueError:
                print("Please enter a valid number")
        
        selected_entity = entities[selected_entity_index]
        entity_id = selected_entity['id']
        entity_name = selected_entity['name']
        
        print(f"\nSelected entity: {entity_name} (ID: {entity_id})")
        
        # Step 3: Choose processing mode
        print("\nProcessing options:")
        print("1. Process from existing document chunks in graph")
        print("2. Process from a document file")
        
        mode = ""
        while mode not in ["1", "2"]:
            mode = input("Select an option (1-2): ")
        
        # Process based on selected mode
        if mode == "1":
            # Process from existing chunks
            print(f"\nFinding document chunks related to '{entity_name}'...")
            document_chunks = get_related_documents(graph, entity_id)
            
            if not document_chunks:
                print(f"No document chunks found related to '{entity_name}'")
                return
            
            print(f"Found {len(document_chunks)} related document chunks")
            
            # Process the entity
            consolidated_entity = process_entity_from_documents(
                graph=graph,
                llm=llm,
                entity_id=entity_id,
                document_chunks=document_chunks
            )
            
        else:
            # Process from document file
            document_files = list_available_documents()
            
            if not document_files:
                print("No document files found in the 'documents' directory")
                custom_path = input("Enter path to a document file: ")
                if os.path.exists(custom_path):
                    document_path = custom_path
                else:
                    print(f"File not found: {custom_path}")
                    return
            else:
                print("\nAvailable documents:")
                for i, path in enumerate(document_files):
                    print(f"{i+1}. {os.path.basename(path)}")
                
                # Get document selection
                selected_doc_index = -1
                while selected_doc_index < 0 or selected_doc_index >= len(document_files):
                    try:
                        selection = input(f"\nSelect a document (1-{len(document_files)}): ")
                        selected_doc_index = int(selection) - 1
                        if selected_doc_index < 0 or selected_doc_index >= len(document_files):
                            print(f"Please enter a number between 1 and {len(document_files)}")
                    except ValueError:
                        print("Please enter a valid number")
                
                document_path = document_files[selected_doc_index]
            
            print(f"\nProcessing entity '{entity_name}' from document: {document_path}")
            
            # Process the entity from the document
            consolidated_entity = process_entity_from_file(
                graph=graph,
                llm=llm,
                entity_id=entity_id,
                document_path=document_path,
                chunk_size=args.chunk_size,
                chunk_overlap=args.chunk_overlap
            )
        
        # Step 4: Save and update results
        if consolidated_entity:
            # Save to file
            save_path = save_extraction_results(consolidated_entity, args.output_dir)
            
            # Update the entity in the graph
            print("\nUpdating entity in the graph...")
            updated_id = update_entity_in_graph(graph, consolidated_entity, entity_id)
            
            print(f"\n✓ Successfully processed entity '{entity_name}'")
            print(f"  Updated entity ID: {updated_id}")
            print(f"  Results saved to: {save_path}")
        else:
            print(f"\n❌ Failed to process entity '{entity_name}'")
    
    # Non-interactive mode with specific entity ID and document
    elif args.entity_id and args.document:
        # Initialize LLM
        try:
            llm = initialize_llm(model_name=args.model, temperature=args.temperature)
        except Exception as e:
            print(f"\nCould not initialize LLM: {e}")
            print("Please ensure Ollama is running and the model is available.")
            return
        
        # Process the entity from the document
        consolidated_entity = process_entity_from_file(
            graph=graph,
            llm=llm,
            entity_id=args.entity_id,
            document_path=args.document,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap
        )
        
        if consolidated_entity:
            # Save to file
            save_path = save_extraction_results(consolidated_entity, args.output_dir)
            
            # Update the entity in the graph
            print("\nUpdating entity in the graph...")
            updated_id = update_entity_in_graph(graph, consolidated_entity, args.entity_id)
            
            print(f"\n✓ Successfully processed entity ID '{args.entity_id}'")
            print(f"  Updated entity ID: {updated_id}")
            print(f"  Results saved to: {save_path}")
        else:
            print(f"\n❌ Failed to process entity ID '{args.entity_id}'")
    
    # Entity ID but no document (process from existing chunks)
    elif args.entity_id:
        # Initialize LLM
        try:
            llm = initialize_llm(model_name=args.model, temperature=args.temperature)
        except Exception as e:
            print(f"\nCould not initialize LLM: {e}")
            print("Please ensure Ollama is running and the model is available.")
            return
        
        # Get entity information
        entity_query = """
        MATCH (e {id: $entity_id})
        RETURN e.id as id, e.name as name
        """
        entity_result = graph.query(entity_query, params={"entity_id": args.entity_id})
        
        if not entity_result:
            print(f"Entity with ID '{args.entity_id}' not found in the graph")
            return
        
        entity_name = entity_result[0]["name"]
        
        # Find related document chunks
        print(f"\nFinding document chunks related to entity '{entity_name}'...")
        document_chunks = get_related_documents(graph, args.entity_id)
        
        if not document_chunks:
            print(f"No document chunks found related to entity '{entity_name}'")
            return
        
        print(f"Found {len(document_chunks)} related document chunks")
        
        # Process the entity
        consolidated_entity = process_entity_from_documents(
            graph=graph,
            llm=llm,
            entity_id=args.entity_id,
            document_chunks=document_chunks
        )
        
        if consolidated_entity:
            # Save to file
            save_path = save_extraction_results(consolidated_entity, args.output_dir)
            
            # Update the entity in the graph
            print("\nUpdating entity in the graph...")
            updated_id = update_entity_in_graph(graph, consolidated_entity, args.entity_id)
            
            print(f"\n✓ Successfully processed entity '{entity_name}'")
            print(f"  Updated entity ID: {updated_id}")
            print(f"  Results saved to: {save_path}")
        else:
            print(f"\n❌ Failed to process entity '{entity_name}'")
    
    else:
        print("\nNo operation specified. Use --interactive or provide --entity-id")
        print("Use --help for more information about available options")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()