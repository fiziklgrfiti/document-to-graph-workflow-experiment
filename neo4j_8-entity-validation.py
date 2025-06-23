# neo4j_entity_validation.py
import os
import argparse
from dotenv import load_dotenv
import warnings
from typing import List, Dict, Any, Tuple, Set
import time
import re
from pathlib import Path
import json

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
        "gemma3:4b",       # Smaller alternative
        "gemma3:12b"       # Fallback option
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

def load_document(document_path: str) -> str:
    """Load document content from file."""
    try:
        with open(document_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ Error loading document {document_path}: {e}")
        return ""

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

def get_entities_by_type(graph: Neo4jGraph, entity_type: str, limit: int = 1000) -> List[Dict[str, Any]]:
    """Get entities of a specific type from the graph."""
    try:
        # Query to get entities of the specified type with their properties
        query = f"""
        MATCH (e:{entity_type})
        RETURN e.id as id, e.name as name, labels(e) as labels
        LIMIT {limit}
        """
        
        result = graph.query(query)
        
        # Process the results
        entities = []
        for record in result:
            entity = {
                "id": record["id"],
                "name": record["name"],
                "type": entity_type,
                "labels": record["labels"] if "labels" in record else [entity_type]
            }
            entities.append(entity)
        
        return entities
    except Exception as e:
        print(f"❌ Error getting entities of type {entity_type}: {e}")
        return []

def get_all_entities(graph: Neo4jGraph) -> List[Dict[str, Any]]:
    """Get all entities from the graph."""
    entity_types = get_entity_types(graph)
    all_entities = []
    
    for entity_type in entity_types:
        try:
            entities = get_entities_by_type(graph, entity_type)
            all_entities.extend(entities)
            print(f"Found {len(entities)} entities of type '{entity_type}'")
        except Exception as e:
            print(f"Error getting entities of type {entity_type}: {e}")
    
    return all_entities

def check_entity_in_document(entity_name: str, document_content: str) -> bool:
    """
    Check if entity name appears in the document.
    Returns True if the entity name is found, False otherwise.
    """
    if not entity_name or not document_content:
        return False
        
    # Convert both to lowercase for case-insensitive matching
    entity_name_lower = entity_name.lower()
    document_content_lower = document_content.lower()
    
    # Check if the entity name appears as a whole word
    # This uses word boundaries to avoid partial matches
    pattern = r'\b' + re.escape(entity_name_lower) + r'\b'
    if re.search(pattern, document_content_lower):
        return True
    
    # If no match with word boundaries, check for a simple substring match
    if entity_name_lower in document_content_lower:
        return True
    
    return False

def check_entity_semantic_match(
    entity_name: str, 
    document_content: str, 
    llm: Ollama,
    chunk_size: int = 1200
) -> bool:
    """
    Perform a semantic analysis to check if the entity is conceptually present in the document.
    This is a more sophisticated check than simple string matching.
    """
    # Create a text splitter for the document
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=200
    )
    
    # Split the document into chunks
    chunks = text_splitter.split_text(document_content)
    
    # Create prompt for semantic analysis
    prompt_template = """
    You are an expert analyst tasked with determining if a specific entity is clearly referenced or implied in a text, 
    even if not mentioned by exact name. There are likely to be concepts that are similiarly named, but you will be 
    able to clearly tell them apart from the specific entity.
    
    ENTITY: {entity_name}
    
    TEXT CHUNK:
    {text_chunk}

    -GOAL-
    Reduce the presence of hallicinations in our dataset.
    
    -TASK-
    Analyze the text chunk and determine if it references or directly implies the entity named above. 
    Consider synonyms, descriptions that CLEARLY match the entity, or unambiguous references.
    
    RESPOND ONLY with either "YES" or "NO":
    - "YES" if the entity is referenced or CLEARLY implied
    - "NO" if there is no clear reference to the entity
    """
    
    prompt = PromptTemplate.from_template(prompt_template)
    chain = prompt | llm | StrOutputParser()
    
    # Check a reasonable number of chunks
    max_chunks_to_check = min(5, len(chunks))
    print(f"Performing semantic analysis on {max_chunks_to_check} chunks...")
    
    for i in range(max_chunks_to_check):
        try:
            chunk = chunks[i]
            # Skip very short chunks
            if len(chunk) < 100:
                continue
                
            # Ask the LLM if this chunk references the entity
            response = chain.invoke({
                "entity_name": entity_name,
                "text_chunk": chunk
            }).strip().upper()
            
            if response == "YES":
                return True
                
        except Exception as e:
            print(f"Error during semantic analysis: {e}")
    
    return False

def get_entity_relationships(graph: Neo4jGraph, entity_id: str) -> List[Dict[str, Any]]:
    """Get all relationships for a specific entity."""
    try:
        # Query to get relationships
        query = """
        MATCH (e {id: $entity_id})-[r]->(target)
        RETURN type(r) as relationship_type, target.id as target_id, target.name as target_name
        UNION
        MATCH (source)-[r]->(e {id: $entity_id})
        RETURN type(r) as relationship_type, source.id as source_id, source.name as source_name
        """
        
        result = graph.query(query, params={"entity_id": entity_id})
        
        return result
    except Exception as e:
        print(f"❌ Error getting relationships for entity {entity_id}: {e}")
        return []

def delete_entity_and_relationships(graph: Neo4jGraph, entity_id: str) -> bool:
    """Delete an entity and its relationships from the graph."""
    try:
        # Delete relationships first
        rel_query = """
        MATCH (e {id: $entity_id})-[r]-()
        DELETE r
        """
        graph.query(rel_query, params={"entity_id": entity_id})
        
        # Then delete the entity
        entity_query = """
        MATCH (e {id: $entity_id})
        DELETE e
        """
        graph.query(entity_query, params={"entity_id": entity_id})
        
        return True
    except Exception as e:
        print(f"❌ Error deleting entity {entity_id}: {e}")
        return False

def generate_validation_report(
    all_entities: List[Dict[str, Any]],
    missing_entities: List[Dict[str, Any]],
    deleted_entities: List[Dict[str, Any]],
    document_path: str
) -> str:
    """Generate a report of the validation process."""
    report = []
    
    report.append("# Entity Validation Report")
    report.append(f"Document: {document_path}")
    report.append(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    report.append("## Summary")
    report.append(f"Total entities checked: {len(all_entities)}")
    report.append(f"Entities not found in document: {len(missing_entities)}")
    report.append(f"Entities deleted: {len(deleted_entities)}")
    report.append("")
    
    if missing_entities:
        report.append("## Entities Not Found in Document")
        for i, entity in enumerate(missing_entities):
            report.append(f"{i+1}. {entity['name']} (ID: {entity['id']}, Type: {entity['type']})")
        report.append("")
    
    if deleted_entities:
        report.append("## Deleted Entities")
        for i, entity in enumerate(deleted_entities):
            report.append(f"{i+1}. {entity['name']} (ID: {entity['id']}, Type: {entity['type']})")
        report.append("")
    
    report.append("## Verification Method")
    report.append("1. String matching: Checking if entity name appears in document")
    report.append("2. Semantic analysis: Using LLM to check if entity is conceptually present")
    
    return "\n".join(report)

def save_report(report: str, output_dir: str = "validation_reports") -> str:
    """Save the validation report to a file."""
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    filename = f"entity_validation_{time.strftime('%Y%m%d_%H%M%S')}.md"
    output_path = os.path.join(output_dir, filename)
    
    # Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✓ Saved validation report to {output_path}")
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

def validate_entities(
    graph: Neo4jGraph, 
    document_path: str, 
    use_semantic_analysis: bool = False,
    llm: Ollama = None,
    entity_types: List[str] = None
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Validate entities against a document to find those that don't appear in the document.
    
    Args:
        graph: Neo4j graph connection
        document_path: Path to the document
        use_semantic_analysis: Whether to use LLM for semantic analysis
        llm: Ollama model for semantic analysis
        entity_types: List of entity types to validate (if None, validate all)
        
    Returns:
        Tuple containing all entities and missing entities
    """
    print(f"\nValidating entities against document: {document_path}")
    
    # Load document content
    document_content = load_document(document_path)
    if not document_content:
        print("❌ Failed to load document content")
        return [], []
        
    print(f"Document loaded: {len(document_content)} characters")
    
    # Get all entities or entities of specific types
    if entity_types:
        all_entities = []
        for entity_type in entity_types:
            all_entities.extend(get_entities_by_type(graph, entity_type))
        print(f"Found {len(all_entities)} entities of types {', '.join(entity_types)}")
    else:
        all_entities = get_all_entities(graph)
        print(f"Found {len(all_entities)} entities of all types")
    
    # Check each entity against the document
    missing_entities = []
    
    print("\nChecking entities against document...")
    for i, entity in enumerate(all_entities):
        entity_name = entity.get("name", "")
        entity_id = entity.get("id", "")
        entity_type = entity.get("type", "Unknown")
        
        # Skip entities without a name
        if not entity_name:
            continue
            
        # String matching check
        if check_entity_in_document(entity_name, document_content):
            continue
        
        # Semantic analysis check if enabled and entity wasn't found by string matching
        if use_semantic_analysis and llm:
            print(f"\nPerforming semantic analysis for entity: {entity_name} ({entity_type})")
            if check_entity_semantic_match(entity_name, document_content, llm):
                print(f"✓ Entity found through semantic analysis: {entity_name}")
                continue
        
        # If we get here, the entity wasn't found
        missing_entities.append(entity)
        
        # Print progress occasionally
        if (i+1) % 10 == 0 or i == len(all_entities) - 1:
            print(f"Progress: {i+1}/{len(all_entities)} entities checked, {len(missing_entities)} missing")
    
    return all_entities, missing_entities

def discover_new_entities(
    document_content: str,
    entity_type: str,
    existing_entities: List[Dict[str, Any]],
    llm: Ollama,
    chunk_size: int = 1500,
    max_entities: int = 5
) -> List[Dict[str, Any]]:
    """
    Discover new entities of a specific type in a document that aren't already in the graph.
    
    Args:
        document_content: The document text
        entity_type: Type of entity to look for
        existing_entities: List of existing entities of this type
        llm: Ollama model for entity extraction
        chunk_size: Size of document chunks to process
        max_entities: Maximum number of new entities to discover
        
    Returns:
        List of discovered entities
    """
    # Create a text splitter for the document
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=200
    )
    
    # Split the document into chunks
    chunks = text_splitter.split_text(document_content)
    print(f"Split document into {len(chunks)} chunks")
    
    # Create a set of existing entity names for faster lookup
    existing_entity_names = {e.get("name", "").lower() for e in existing_entities if e.get("name")}
    print(f"Found {len(existing_entity_names)} existing {entity_type} entities to exclude")
    
    # Format existing entities for the prompt
    existing_entities_list = ", ".join([f"'{e.get('name', '')}'" for e in existing_entities if e.get("name")])
    if len(existing_entities_list) > 1000:
        # Truncate if too long for the prompt
        existing_entities_list = existing_entities_list[:1000] + "... and more"
    
    # Create prompt for entity discovery
    prompt_template = """
    You are an expert entity extractor. Your task is to identify NEW entities of a specific type in the text.
    
    ENTITY TYPE: {entity_type}
    
    EXISTING ENTITIES (DO NOT INCLUDE THESE):
    {existing_entities}
    
    TEXT CHUNK:
    {text_chunk}
    
    TASK:
    Identify any entities of type "{entity_type}" in the text that are NOT in the list of existing entities.
    Look for clear, explicit mentions of {entity_type} entities.
    
    For each NEW entity found, provide:
    1. The name of the entity
    2. A brief description or context from the text
    3. The exact text snippet where it was mentioned
    
    Return your findings in this JSON format:
    {{
      "entities": [
        {{
          "name": "Entity Name",
          "description": "Brief description based on context",
          "text_snippet": "... text where the entity was mentioned ..."
        }},
        ...
      ]
    }}
    
    If no new entities are found, return: {{"entities": []}}
    
    Respond ONLY with valid JSON.
    """
    
    prompt = PromptTemplate.from_template(prompt_template)
    chain = prompt | llm | StrOutputParser()
    
    # Process each chunk
    discovered_entities = []
    chunks_with_discoveries = 0
    
    print(f"Searching for new {entity_type} entities across document chunks...")
    for i, chunk in enumerate(chunks):
        if len(discovered_entities) >= max_entities:
            print(f"Reached maximum of {max_entities} new entities. Stopping search.")
            break
            
        print(f"\nProcessing chunk {i+1}/{len(chunks)}...")
        
        try:
            # Skip very short chunks
            if len(chunk) < 100:
                continue
                
            # Process the chunk with LLM
            response = chain.invoke({
                "entity_type": entity_type,
                "existing_entities": existing_entities_list,
                "text_chunk": chunk
            })
            
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                try:
                    result = json.loads(json_str)
                    entities = result.get("entities", [])
                    
                    # Filter out any entities that somehow match existing ones
                    new_entities = []
                    for entity in entities:
                        entity_name = entity.get("name", "")
                        if entity_name and entity_name.lower() not in existing_entity_names:
                            # Add chunk index for reference
                            entity["chunk_index"] = i
                            new_entities.append(entity)
                    
                    if new_entities:
                        chunks_with_discoveries += 1
                        print(f"  ✓ Found {len(new_entities)} potential new entities in chunk {i+1}")
                        discovered_entities.extend(new_entities)
                except json.JSONDecodeError as e:
                    print(f"  ❌ Error parsing JSON: {e}")
            
        except Exception as e:
            print(f"  ❌ Error processing chunk {i+1}: {e}")
    
    print(f"\nDiscovery complete. Found {len(discovered_entities)} potential new entities in {chunks_with_discoveries} chunks.")
    return discovered_entities

def verify_and_add_entities(
    discovered_entities: List[Dict[str, Any]],
    entity_type: str,
    graph: Neo4jGraph,
    document_content: str
) -> List[Dict[str, Any]]:
    """
    Present discovered entities to the user for verification and add confirmed ones to the graph.
    
    Args:
        discovered_entities: List of discovered entities
        entity_type: Type of entity
        graph: Neo4j graph connection
        document_content: Full document content for context
        
    Returns:
        List of entities that were added to the graph
    """
    if not discovered_entities:
        print("No new entities discovered.")
        return []
    
    added_entities = []
    
    print(f"\n{'='*60}")
    print(f"VERIFICATION OF NEW {entity_type.upper()} ENTITIES")
    print(f"{'='*60}")
    print(f"Found {len(discovered_entities)} potential new entities of type '{entity_type}'.")
    print("Each will be presented for verification before adding to the graph.")
    
    # Process each entity
    for i, entity in enumerate(discovered_entities):
        entity_name = entity.get("name", "")
        description = entity.get("description", "")
        text_snippet = entity.get("text_snippet", "")
        chunk_index = entity.get("chunk_index", -1)
        
        print(f"\n{'='*60}")
        print(f"ENTITY {i+1}/{len(discovered_entities)}: {entity_name}")
        print(f"{'='*60}")
        print(f"Description: {description}")
        print(f"\nContext:")
        print(f"-------")
        print(text_snippet)
        print(f"-------")
        
        # Ask for verification
        confirmation = input(f"\nAdd this entity to the graph? (y/n) [y]: ")
        if confirmation.lower() != 'n':
            # Generate a unique ID for the entity
            entity_id = f"{entity_name.lower().replace(' ', '_')}_{int(time.time() % 10000)}"
            
            # Add entity to the graph
            try:
                query = f"""
                CREATE (e:{entity_type} {{
                    id: $id,
                    name: $name,
                    description: $description,
                    source_text: $text_snippet
                }})
                RETURN e.id as id
                """
                
                result = graph.query(query, params={
                    "id": entity_id,
                    "name": entity_name,
                    "description": description,
                    "text_snippet": text_snippet
                })
                
                if result:
                    print(f"✓ Added entity '{entity_name}' to graph with ID: {entity_id}")
                    entity["id"] = entity_id
                    added_entities.append(entity)
                else:
                    print(f"❌ Failed to add entity '{entity_name}' to graph")
            except Exception as e:
                print(f"❌ Error adding entity to graph: {e}")
        else:
            print(f"× Skipped adding entity '{entity_name}' to graph")
            
        # Check if user wants to continue
        if i < len(discovered_entities) - 1:  # Not the last entity
            continue_option = input("\nContinue to next entity? (y/n) [y]: ")
            if continue_option.lower() == 'n':
                print(f"\nStopping verification. Processed {i+1} out of {len(discovered_entities)} entities.")
                break
    
    # Report results
    if added_entities:
        print(f"\n✓ Added {len(added_entities)} new entities to the graph:")
        for entity in added_entities:
            print(f"  - {entity['name']} (ID: {entity['id']})")
    else:
        print("\nNo entities were added to the graph.")
    
    return added_entities

def generate_discovery_report(
    entity_type: str,
    discovered_entities: List[Dict[str, Any]],
    added_entities: List[Dict[str, Any]],
    document_path: str
) -> str:
    """Generate a report of the entity discovery process."""
    report = []
    
    report.append("# Entity Discovery Report")
    report.append(f"Document: {document_path}")
    report.append(f"Entity Type: {entity_type}")
    report.append(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    report.append("## Summary")
    report.append(f"Potential new entities discovered: {len(discovered_entities)}")
    report.append(f"Entities added to graph: {len(added_entities)}")
    report.append("")
    
    if discovered_entities:
        report.append("## Discovered Entities")
        for i, entity in enumerate(discovered_entities):
            was_added = any(e.get('name') == entity.get('name') for e in added_entities)
            status = "✓ Added" if was_added else "× Skipped"
            report.append(f"{i+1}. {entity['name']} - {status}")
            report.append(f"   Description: {entity.get('description', 'N/A')}")
            if 'text_snippet' in entity:
                snippet = entity['text_snippet'].replace('\n', ' ').strip()
                # Truncate long snippets
                if len(snippet) > 200:
                    snippet = snippet[:197] + "..."
                report.append(f"   Context: \"{snippet}\"")
            report.append("")
    
    if added_entities:
        report.append("## Next Steps")
        report.append("Consider running the entity-focused extraction process for these new entities:")
        for entity in added_entities:
            report.append(f"- `python neo4j_7-neo4j_entity_focused_extraction.py --entity-id {entity.get('id')}`")
        report.append("")
    
    return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="Validate entities in Neo4j against a document")
    
    # Document selection
    parser.add_argument("--document", help="Path to document file to validate against")
    
    # Entity filtering
    parser.add_argument("--entity-type", help="Validate only entities of this type")
    parser.add_argument("--all-types", action="store_true", help="Validate entities of all types")
    
    # Analysis options
    parser.add_argument("--semantic", action="store_true", help="Use semantic analysis for validation")
    parser.add_argument("--model", default="gemma3:4b", help="LLM model for semantic analysis")
    
    # Action options
    parser.add_argument("--delete", action="store_true", help="Delete entities not found in document")
    parser.add_argument("--report", action="store_true", help="Generate validation report")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    
    # Discover new 
    parser.add_argument("--discover", action="store_true", help="Discover new entities in document")
    parser.add_argument("--max-entities", type=int, default=5, help="Maximum number of new entities to discover")

    args = parser.parse_args()
    
    # Initialize Neo4j connection
    try:
        graph = initialize_neo4j_connection()
    except Exception as e:
        print(f"\nCould not connect to Neo4j: {e}")
        print("Please ensure Neo4j is running and credentials are correct.")
        return
    
    # Initialize LLM if semantic analysis is enabled
    llm = None
    if args.semantic:
        try:
            llm = initialize_llm(model_name=args.model)
        except Exception as e:
            print(f"\nCould not initialize LLM: {e}")
            print("Semantic analysis will be disabled.")
    
    # Interactive mode
    if args.interactive:
        print("\n" + "="*60)
        print("ENTITY VALIDATION AGAINST DOCUMENT")
        print("="*60)
        
        # Step 1: Select document
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
        
        print(f"\nSelected document: {document_path}")
        
        # Step 2: Select entity types to validate
        entity_types = get_entity_types(graph)
        
        print("\nAvailable entity types:")
        for i, entity_type in enumerate(entity_types):
            print(f"{i+1}. {entity_type}")
        
        print(f"{len(entity_types)+1}. All entity types")
        
        # Get entity type selection
        selected_type_option = -1
        while selected_type_option < 1 or selected_type_option > len(entity_types) + 1:
            try:
                selection = input(f"\nSelect entity types to validate (1-{len(entity_types)+1}): ")
                selected_type_option = int(selection)
                if selected_type_option < 1 or selected_type_option > len(entity_types) + 1:
                    print(f"Please enter a number between 1 and {len(entity_types)+1}")
            except ValueError:
                print("Please enter a valid number")
        
        selected_entity_types = None
        if selected_type_option <= len(entity_types):
            selected_entity_types = [entity_types[selected_type_option - 1]]
            print(f"\nValidating entities of type: {selected_entity_types[0]}")
        else:
            print("\nValidating entities of all types")
        
        # Step 3: Select operation mode
        print("\nOperation mode:")
        print("1. Validate existing entities (find hallucinations)")
        print("2. Discover new entities")
        print("3. Both validate and discover")
        
        operation_mode = ""
        while operation_mode not in ["1", "2", "3"]:
            operation_mode = input("Select operation mode (1-3): ")
        
        do_validation = operation_mode in ["1", "3"]
        do_discovery = operation_mode in ["2", "3"]

        # Initialize variables that might be used later
        missing_entities = []
        all_entities = []
        deleted_entities = []
        
        # If discovery is selected, proceed with discovery process
        if do_discovery:
            # Load document content
            document_content = load_document(document_path)
            if not document_content:
                print("❌ Failed to load document content")
                return
            
            # Get existing entities of the selected type
            existing_entities = get_entities_by_type(graph, selected_entity_types[0])
            
            # Configure max entities
            max_entities = args.max_entities
            print(f"\nMaximum new entities to discover: {max_entities}")
            change_max = input("Change this limit? (y/n): ").lower() == 'y'
            if change_max:
                try:
                    new_max = int(input(f"Enter new maximum (1-20): "))
                    max_entities = max(1, min(20, new_max))
                    print(f"Set maximum to {max_entities}")
                except ValueError:
                    print(f"Invalid value. Using default: {max_entities}")
            
            # Initialize LLM if not already done
            if not llm:
                print("\nInitializing LLM for entity discovery...")
                try:
                    llm = initialize_llm(model_name=args.model)
                except Exception as e:
                    print(f"\nCould not initialize LLM: {e}")
                    print("Entity discovery will be skipped.")
                    do_discovery = False
            
            if do_discovery:
                # Discover new entities
                discovered_entities = discover_new_entities(
                    document_content=document_content,
                    entity_type=selected_entity_types[0],
                    existing_entities=existing_entities,
                    llm=llm,
                    max_entities=max_entities
                )
                
                # Verify and add entities
                if discovered_entities:
                    added_entities = verify_and_add_entities(
                        discovered_entities=discovered_entities,
                        entity_type=selected_entity_types[0],
                        graph=graph,
                        document_content=document_content
                    )
                    
                    # Generate report
                    if discovered_entities:
                        report = generate_discovery_report(
                            entity_type=selected_entity_types[0],
                            discovered_entities=discovered_entities,
                            added_entities=added_entities,
                            document_path=document_path
                        )
                        
                        report_path = save_report(report, "discovery_reports")
                        print(f"\nDiscovery report saved to: {report_path}")
                        
                        # Suggest next steps
                        if added_entities:
                            print("\nNext Steps:")
                            print("Consider running entity-focused extraction for these new entities:")
                            for entity in added_entities:
                                entity_id = entity.get("id", "")
                                entity_name = entity.get("name", "")
                                if entity_id:
                                    print(f"  python neo4j_7-neo4j_entity_focused_extraction.py --entity-id {entity_id}")
                else:
                    print("\nNo new entities discovered.")
        
        # If validation is selected, proceed with the existing validation code
        if do_validation:
            use_semantic = input("\nUse semantic analysis for validation? (y/n): ").lower() == 'y'
            
            if use_semantic and not llm:
                print("\nInitializing LLM for semantic analysis...")
                try:
                    llm = initialize_llm(model_name=args.model)
                except Exception as e:
                    print(f"\nCould not initialize LLM: {e}")
                    print("Semantic analysis will be disabled.")
                    use_semantic = False
            
            # Step 4: Validate entities
            all_entities, missing_entities = validate_entities(
                graph=graph,
                document_path=document_path,
                use_semantic_analysis=use_semantic,
                llm=llm,
                entity_types=selected_entity_types
            )
        
        # Step 5: Show results and ask for deletion
        if do_validation and missing_entities:
            print(f"\nFound {len(missing_entities)} entities not mentioned in the document:")
            for i, entity in enumerate(missing_entities):
                print(f"{i+1}. {entity['name']} (Type: {entity['type']})")
            
            delete_option = input("\nDelete these entities? (y/n): ").lower()
            
            if delete_option == 'y':
                deleted_entities = []
                
                for entity in missing_entities:
                    entity_id = entity.get("id")
                    entity_name = entity.get("name")
                    
                    print(f"\nDeleting entity: {entity_name} (ID: {entity_id})")
                    
                    # Get relationships before deleting
                    relationships = get_entity_relationships(graph, entity_id)
                    if relationships:
                        print(f"  This entity has {len(relationships)} relationships:")
                        for rel in relationships[:5]:  # Show first 5 relationships
                            if "target_name" in rel:
                                print(f"  - {entity_name} [{rel['relationship_type']}] -> {rel['target_name']}")
                            elif "source_name" in rel:
                                print(f"  - {rel['source_name']} [{rel['relationship_type']}] -> {entity_name}")
                        
                        if len(relationships) > 5:
                            print(f"  - ... and {len(relationships) - 5} more")
                    
                    # Delete the entity
                    if delete_entity_and_relationships(graph, entity_id):
                        print(f"✓ Entity deleted: {entity_name}")
                        deleted_entities.append(entity)
                    else:
                        print(f"❌ Failed to delete entity: {entity_name}")
                
                print(f"\n✓ Deleted {len(deleted_entities)} out of {len(missing_entities)} missing entities")
                
                # Generate report
                report = generate_validation_report(
                    all_entities=all_entities,
                    missing_entities=missing_entities,
                    deleted_entities=deleted_entities,
                    document_path=document_path
                )
                
                save_report(report)
            else:
                print("\nNo entities were deleted.")
                
                # Generate report without deletions
                report = generate_validation_report(
                    all_entities=all_entities,
                    missing_entities=missing_entities,
                    deleted_entities=[],
                    document_path=document_path
                )
                
                save_report(report)
        elif do_validation:
            print("\nAll entities were found in the document!")
    
    # Non-interactive mode
    else:
        # Validate arguments
        if not args.document:
            print("Please specify a document with --document")
            return
                
        if not os.path.exists(args.document):
            print(f"Document not found: {args.document}")
            return
        
        # Handle different modes
        if args.discover:
            # Determine entity types to validate
            selected_entity_types = None
            if args.entity_type:
                selected_entity_types = [args.entity_type]
                print(f"Discovering new entities of type: {args.entity_type}")
            else:
                print("Please specify an entity type with --entity-type")
                return
                    
            # Load document content
            document_content = load_document(args.document)
            if not document_content:
                print("❌ Failed to load document content")
                return
            
            # Get existing entities of the selected type
            existing_entities = get_entities_by_type(graph, selected_entity_types[0])
            
            # Initialize LLM
            try:
                if not llm:
                    llm = initialize_llm(model_name=args.model)
            except Exception as e:
                print(f"\nCould not initialize LLM: {e}")
                return
            
            # Discover new entities
            discovered_entities = discover_new_entities(
                document_content=document_content,
                entity_type=selected_entity_types[0],
                existing_entities=existing_entities,
                llm=llm,
                max_entities=args.max_entities
            )
            
            # Verify and add entities
            if discovered_entities:
                added_entities = verify_and_add_entities(
                    discovered_entities=discovered_entities,
                    entity_type=selected_entity_types[0],
                    graph=graph,
                    document_content=document_content
                )
                
                # Generate report
                if discovered_entities:
                    report = generate_discovery_report(
                        entity_type=selected_entity_types[0],
                        discovered_entities=discovered_entities,
                        added_entities=added_entities,
                        document_path=args.document
                    )
                    
                    save_report(report, "discovery_reports")
            else:
                print("\nNo new entities discovered.")
        else:
            # Determine entity types to validate
            selected_entity_types = None
            if args.entity_type:
                selected_entity_types = [args.entity_type]
                print(f"Validating entities of type: {args.entity_type}")
            elif args.all_types:
                print("Validating entities of all types")
            else:
                print("Please specify --entity-type or --all-types")
                return
                    
            # Validate entities
            all_entities, missing_entities = validate_entities(
                graph=graph,
                document_path=args.document,
                use_semantic_analysis=args.semantic,
                llm=llm,
                entity_types=selected_entity_types
            )
            
            # Delete entities if requested
            deleted_entities = []
            if args.delete and missing_entities:
                print(f"\nDeleting {len(missing_entities)} entities not found in document...")
                
                for entity in missing_entities:
                    entity_id = entity.get("id")
                    entity_name = entity.get("name")
                    
                    if delete_entity_and_relationships(graph, entity_id):
                        print(f"✓ Entity deleted: {entity_name}")
                        deleted_entities.append(entity)
                    else:
                        print(f"❌ Failed to delete entity: {entity_name}")
                        
                print(f"\n✓ Deleted {len(deleted_entities)} out of {len(missing_entities)} missing entities")
            
            # Generate report if requested
            if args.report:
                report = generate_validation_report(
                    all_entities=all_entities,
                    missing_entities=missing_entities,
                    deleted_entities=deleted_entities,
                    document_path=args.document
                )
                
                save_report(report)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()