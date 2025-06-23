# neo4j_document_processor.py
import os
from pathlib import Path
from dotenv import load_dotenv
import warnings
from typing import List, Dict, Any, Optional, Union
import json
import concurrent.futures
import time
import tqdm  # For progress bars
import pickle  # For saving/loading extracted data
import hashlib  # For generating unique ids for chunks
import threading  # For thread-safe progress updates
import signal  # For handling timeouts
import contextlib  # For timeout context manager

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

# For verbose output tracking
verbose_extraction = False
extraction_step_lock = threading.Lock()
extraction_steps = {}

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
    """Load document from various file types and return as LangChain documents."""
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

# Timeout context manager
class TimeoutError(Exception):
    pass

@contextlib.contextmanager
def timeout(seconds):
    def signal_handler(signum, frame):
        raise TimeoutError(f"Timed out after {seconds} seconds")
    
    original_handler = signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, original_handler)

# Helper function to update extraction step
def update_extraction_step(chunk_idx, step, details=None):
    """Update the current extraction step for a chunk."""
    if not verbose_extraction:
        return
    
    with extraction_step_lock:
        extraction_steps[chunk_idx] = (step, details)

# LLM-based extraction with detailed progress tracking
def extract_entities_relationships(text_chunk: str, chunk_idx: int = -1, max_attempts: int = 2) -> Dict[str, Any]:
    """Use LLM to extract entities, relationships, and properties from text with robust parsing."""
    
    # Initialize extraction step
    update_extraction_step(chunk_idx, "Starting extraction")
    
    # Initialize a fresh Ollama instance each time this function is called
    # This ensures each process gets its own LLM instance
    try:
        update_extraction_step(chunk_idx, "Initializing LLM")
        llm = Ollama(model="llama3.1:latest", temperature=0.3)
    except Exception as e:
        update_extraction_step(chunk_idx, f"LLM init error: {str(e)[:30]}...")
        print(f"\nError initializing LLM for chunk {chunk_idx+1}: {e}")
        return {"entities": [], "relationships": []}
    
    prompt_template = """
    You are a specialized AI trained to extract entities & relationships from documents.
    Specifically you can quickly & accurate extract C2M2 "objectives" (also known as "practices") from the Cybersecurity Capability Maturity Model (C2M2).
    You're also able to associate the "domain" that these objectives belong to as a relationship.

    -Goal-
    Given a C2M2 output file quickly & accurately identify all C2M2 domains & objectives, as entities and relationships of a graph. 
    A detailed extraction will be run seperate to this initial extraction.

    -Steps-
    1. Analyze the text and extract:
        i. ENTITIES: Identify all significant entities (domains, objectives).
            - entity_name: Name of the entity, capitalized
            - entity_type: Entity type (objective or practice)
        
        ii. RELATIONSHIPS: Identify relationships between these entities 
            From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other.
            That said, it's better to have fewer, high-confidence relationships than many speculative ones.
            For each pair of related entities, extract the following information:
            - source_entity: name of the source entity, as identified in step 1
            - target_entity: name of the target entity, as identified in step 1
            - relationship_description: explanation as to why you think the source entity and the target entity are related to each other
            - relationship_strength: a numeric score indicating strength of the relationship between the source entity and target entity
    
        iii. PROPERTIES: Extract attributes/properties for each entity
            - properties: Such as comprehensive description of the entity's attributes, activities or special qualities. 

    2. IMPORTANT: Your response MUST be valid JSON with this exact structure, for example:
    {{
    "entities": [
        {{
        "id": "unique_identifier",
        "type": "domain/practice/concept/etc",
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
    3. Ensure entity IDs are unique and used consistently for relationships.
    4. Double-check that your JSON is valid - all quotes must be closed, all commas must be in the right places.
    5. Once the JSON is valid, review the identified entities & relationships to ensure all items have been identified.

    Text:
    {text}

    Return only valid, parseable JSON. Do not include any explanation or comments outside the JSON structure.
    """
    
    update_extraction_step(chunk_idx, "Creating prompt")
    prompt = PromptTemplate.from_template(prompt_template)
    
    # Create chain
    chain = prompt | llm | StrOutputParser()
    
    # Add a timeout mechanism
    for attempt in range(max_attempts):
        try:
            update_extraction_step(chunk_idx, f"Attempt {attempt+1}/{max_attempts}: Sending to LLM")
            
            # Use a shorter timeout for subsequent attempts
            timeout_seconds = 1200 if attempt == 0 else 120
            
            # Run LLM with timeout
            try:
                # Note: Using context manager timeout might not work with all async operations
                # So we're implementing a manual timeout approach
                start_time = time.time()
                result_future = concurrent.futures.ThreadPoolExecutor(max_workers=1).submit(
                    chain.invoke, {"text": text_chunk}
                )
                
                # Wait for the result with a timeout
                result_text = result_future.result(timeout=timeout_seconds)
                
                # If we got here, the LLM completed successfully
                update_extraction_step(chunk_idx, f"LLM completed in {time.time() - start_time:.2f}s")
                
            except concurrent.futures.TimeoutError:
                update_extraction_step(chunk_idx, f"LLM timeout after {timeout_seconds}s")
                print(f"\nTimeout in LLM processing for chunk {chunk_idx+1}")
                
                # Cancel the task if possible
                if not result_future.done():
                    result_future.cancel()
                
                # If this is the last attempt, return empty result
                if attempt == max_attempts - 1:
                    return {"entities": [], "relationships": []}
                
                # Try again with the next attempt
                continue
            
            # Find JSON in the result
            update_extraction_step(chunk_idx, "Parsing JSON response")
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = result_text[json_start:json_end]
                
                # Attempt to fix common JSON errors
                try:
                    # 1. Try parsing as-is first
                    update_extraction_step(chunk_idx, "Parsing JSON (initial attempt)")
                    data = json.loads(json_str)
                    update_extraction_step(chunk_idx, f"Success! Found {len(data.get('entities', []))} entities")
                    return data
                except json.JSONDecodeError as je:
                    # Log the error but continue with repair attempts
                    update_extraction_step(chunk_idx, f"JSON error: {str(je)[:30]}...")
                    print(f"\nInitial JSON parsing error in chunk {chunk_idx+1}: {je}, attempting fixes...")
                    
                    # 2. Try to fix common JSON errors
                    update_extraction_step(chunk_idx, "Attempting JSON fixes")
                    
                    # Fix unescaped quotes within strings
                    fixed_json = json_str
                    
                    # Fix trailing commas in arrays/objects
                    fixed_json = fixed_json.replace(",]", "]").replace(",}", "}")
                    
                    try:
                        data = json.loads(fixed_json)
                        update_extraction_step(chunk_idx, f"Fixed JSON! Found {len(data.get('entities', []))} entities")
                        print(f"\nFixed JSON successfully for chunk {chunk_idx+1}!")
                        return data
                    except json.JSONDecodeError:
                        update_extraction_step(chunk_idx, "JSON fix failed")
                        # If we're on the last attempt, return empty structure
                        if attempt == max_attempts - 1:
                            print(f"\nFailed to parse JSON after {max_attempts} attempts for chunk {chunk_idx+1}")
                            return {"entities": [], "relationships": []}
                        # Otherwise, try again with a different approach
                        continue
            else:
                update_extraction_step(chunk_idx, "No valid JSON found in response")
                print(f"\nNo valid JSON found in LLM response for chunk {chunk_idx+1}")
                if attempt == max_attempts - 1:
                    return {"entities": [], "relationships": []}
                    
        except Exception as e:
            update_extraction_step(chunk_idx, f"Error: {str(e)[:30]}...")
            print(f"\nError extracting entities and relationships with LLM for chunk {chunk_idx+1}: {e}")
            # If we're on the last attempt, return empty structure
            if attempt == max_attempts - 1:
                return {"entities": [], "relationships": []}
            # Otherwise, try again
            time.sleep(1)  # Brief pause before retry
            continue
    
    # Return empty structure if all parsing attempts fail
    update_extraction_step(chunk_idx, "All attempts failed, returning empty result")
    return {"entities": [], "relationships": []}

# Build Neo4j graph
def build_graph(graph: Neo4jGraph, extracted_data: Dict[str, Any], clear_existing: bool = True):
    """Build Neo4j graph from extracted entities and relationships."""
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
    """Save extracted data to a file."""
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    with open(output_file, 'wb') as f:
        pickle.dump(data_list, f)
    print(f"✓ Saved extracted data to {output_file}")

# Function to load extracted data
def load_extracted_data(input_file: str) -> List[Dict[str, Any]]:
    """Load extracted data from a file."""
    if not os.path.exists(input_file):
        print(f"❌ No saved data found at {input_file}")
        return []
        
    with open(input_file, 'rb') as f:
        data_list = pickle.load(f)
    print(f"✓ Loaded extracted data from {input_file} ({len(data_list)} chunks)")
    return data_list

# Get default output file path for extracted data
def get_default_output_file(document_path: str) -> str:
    """Get default output file path for extracted data."""
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

# Function to process a single chunk with better timeouts
def process_chunk(chunk, chunk_index, total_chunks, max_retries=3):
    """Process a single document chunk with improved timeout handling."""
    retry_count = 0
    while retry_count <= max_retries:
        try:
            text = chunk.page_content
            
            # If this is a retry, print that information
            if retry_count > 0:
                print(f"Retry attempt {retry_count}/{max_retries} for chunk {chunk_index+1}")
            
            # Extract entities and relationships with the chunk index for tracking
            extracted_data = extract_entities_relationships(text, chunk_index, max_attempts=2)
            
            # Check what was found in this chunk
            entity_count = len(extracted_data.get("entities", []))
            relationship_count = len(extracted_data.get("relationships", []))
            
            # Only return if we found something
            if entity_count > 0 or relationship_count > 0:
                print(f"\nChunk {chunk_index+1}: Found {entity_count} entities and {relationship_count} relationships")
                # Clean up extraction step tracking
                with extraction_step_lock:
                    if chunk_index in extraction_steps:
                        del extraction_steps[chunk_index]
                return extracted_data
            else:
                print(f"\nChunk {chunk_index+1}: No entities or relationships found")
                retry_count += 1
                if retry_count > max_retries:
                    # Clean up extraction step tracking
                    with extraction_step_lock:
                        if chunk_index in extraction_steps:
                            del extraction_steps[chunk_index]
                    return None
                time.sleep(1)  # Wait before retry
            
        except Exception as e:
            print(f"\nError processing chunk {chunk_index+1}: {e}")
            retry_count += 1
            if retry_count <= max_retries:
                time.sleep(2)  # Wait before retrying
            else:
                # Clean up extraction step tracking
                with extraction_step_lock:
                    if chunk_index in extraction_steps:
                        del extraction_steps[chunk_index]
                return None

# Determine optimal chunk size based on document size
def get_optimal_chunk_settings(document_path: str) -> tuple:
    """Determine optimal chunk size and overlap based on document size."""
    try:
        # Get file size in bytes
        file_size = os.path.getsize(document_path)
        
        # Convert to KB
        file_size_kb = file_size / 1024
        
        # Determine optimal settings based on file size
        if file_size_kb < 500:  # Small document (< 500 KB)
            return 800, 100
        elif file_size_kb < 1000:  # Medium document (500 KB - 1 MB)
            return 1200, 150
        elif file_size_kb < 5000:  # Large document (1 MB - 5 MB)
            return 1800, 200
        else:  # Very large document (> 5 MB)
            return 2500, 300
    except Exception as e:
        print(f"Error determining optimal chunk size: {e}. Using default values.")
        return 1000, 100

def process_chunk_wrapper(args):
    """Wrapper function for processing a chunk in parallel."""
    chunk, idx, total = args
    try:
        result = process_chunk(chunk, idx, total)
        return idx, result
    except Exception as e:
        print(f"\nError in worker processing chunk {idx}: {str(e)}")
        # Clean up extraction step tracking
        with extraction_step_lock:
            if idx in extraction_steps:
                del extraction_steps[idx]
        return idx, None

# Progress tracking class with improvements
class ProgressTracker:
    """Thread-safe progress tracker for parallel processing."""
    def __init__(self, total_chunks):
        self.total_chunks = total_chunks
        self.processed_chunks = 0
        self.successful_chunks = 0
        self.entity_count = 0
        self.relationship_count = 0
        self.lock = threading.Lock()
        
        # Create progress bar
        self.progress_bar = tqdm.tqdm(total=total_chunks, desc="Processing chunks")
        
        # Create a separate display for chunk status
        if verbose_extraction:
            self.status_display = {}
            for idx in range(total_chunks):
                self.status_display[idx] = "Pending"
        
        # Track active chunks with timestamps for detecting hangs
        self.active_chunks = {}
        self.hang_threshold = 300  # 5 minutes in seconds
        
        # Last print time to avoid too frequent updates
        self.last_print_time = 0
        self.print_interval = 2  # seconds

    # Helper function to update extraction step
    def update(self, chunk_idx, result):
        """Update progress tracker with a processed chunk result."""
        with self.lock:
            self.processed_chunks += 1
            
            # Remove from active chunks
            if chunk_idx in self.active_chunks:
                del self.active_chunks[chunk_idx]
            
            # Also remove from extraction_steps to keep it clean
            with extraction_step_lock:
                if chunk_idx in extraction_steps:
                    del extraction_steps[chunk_idx]
            
            # Update progress bar
            self.progress_bar.update(1)
            
            # Update chunk status
            if verbose_extraction:
                if result:
                    entity_count = len(result.get("entities", []))
                    relationship_count = len(result.get("relationships", []))
                    self.entity_count += entity_count
                    self.relationship_count += relationship_count
                    self.successful_chunks += 1
                    self.status_display[chunk_idx] = f"✓ Found {entity_count} entities, {relationship_count} relationships"
                else:
                    self.status_display[chunk_idx] = "❌ Failed"
            
            # Only print full status at intervals to avoid flooding the console
            current_time = time.time()
            if verbose_extraction and (current_time - self.last_print_time) > self.print_interval:
                self._print_status()
                self.last_print_time = current_time
    
    def mark_chunk_active(self, chunk_idx):
        """Mark a chunk as currently being processed with timestamp."""
        with self.lock:
            self.active_chunks[chunk_idx] = time.time()
            if verbose_extraction:
                self.status_display[chunk_idx] = "⚙️ Processing"
                
                # Print status update
                current_time = time.time()
                if (current_time - self.last_print_time) > self.print_interval:
                    self._print_status()
                    self.last_print_time = current_time
    
    def check_for_hangs(self):
        """Check for chunks that might be hanging and report them."""
        with self.lock:
            current_time = time.time()
            hung_chunks = []
            
            for chunk_idx, start_time in self.active_chunks.items():
                # Only consider chunks that have an entry in extraction_steps
                if chunk_idx in extraction_steps:
                    elapsed = current_time - start_time
                    if elapsed > self.hang_threshold:
                        hung_chunks.append((chunk_idx, elapsed))
            
            if hung_chunks:
                print("\nPotentially hanging chunks detected:")
                for chunk_idx, elapsed in hung_chunks:
                    chunk_status = "Unknown"
                    if chunk_idx in extraction_steps:
                        step, details = extraction_steps[chunk_idx]
                        chunk_status = f"{step}"
                        if details:
                            chunk_status += f" - {details}"
                    
                    print(f"  Chunk {chunk_idx+1}: Running for {elapsed:.1f} seconds. Status: {chunk_status}")
                
                # Return the list of hung chunks for possible intervention
                return hung_chunks
            
            return []

    def _print_status(self):
        """Print the current status of all chunks."""
        # Clear screen if supported
        if os.name == 'posix':
            os.system('clear')
        elif os.name == 'nt':
            os.system('cls')
        
        # Print header
        print(f"\n{'='*80}")
        print(f"DOCUMENT EXTRACTION PROGRESS")
        print(f"{'='*80}")
        
        # Print overall progress
        percent = int((self.processed_chunks / self.total_chunks) * 100)
        success_rate = int((self.successful_chunks / self.processed_chunks) * 100) if self.processed_chunks > 0 else 0
        
        print(f"\nProgress: {self.processed_chunks}/{self.total_chunks} ({percent}%)")
        print(f"Success: {self.successful_chunks}/{self.processed_chunks} ({success_rate}%)")
        print(f"Found: {self.entity_count} entities, {self.relationship_count} relationships\n")
        
        # Print active chunks status
        print(f"{'='*80}")
        print(f"ACTIVE CHUNKS STATUS")
        print(f"{'='*80}\n")
        
        # Only display information for chunks that are in extraction_steps and active_chunks
        active_chunk_keys = sorted(set(extraction_steps.keys()) & set(self.active_chunks.keys()))
        
        if active_chunk_keys:
            for idx in active_chunk_keys:
                step, details = extraction_steps.get(idx, ("Unknown", None))
                status_line = f"Chunk {idx+1}: {step}"
                if details:
                    status_line += f" - {details}"
                print(status_line)
        else:
            print("No active chunks at the moment.")
        
        print(f"\n{'='*80}")


    def close(self):
        """Close progress displays."""
        self.progress_bar.close()

# Main function to process documents and build graph with improved error handling and timeout detection
def process_document_to_graph(
    document_path: str, 
    chunk_size: int = None, 
    chunk_overlap: int = None, 
    clear_existing: bool = True,
    parallel: bool = False,
    max_workers: int = 4,
    verbose: bool = True,
    start_chunk: int = 0,
    end_chunk: Optional[int] = None,
    save_data: bool = False,
    load_data: bool = False,
    output_file: Optional[str] = None,
    adaptive_chunking: bool = True,
    log_file: Optional[str] = None,
    extraction_verbose: bool = False
):
    """Process document and build Neo4j graph."""
    global verbose_extraction
    verbose_extraction = extraction_verbose
    
    print(f"\n{'='*50}")
    print(f"DOCUMENT TO GRAPH PROCESSING: {os.path.basename(document_path)}")
    print(f"{'='*50}\n")
    
    # Set up logging if requested
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_handle = open(log_file, 'w')
        def log_message(msg):
            log_handle.write(f"{msg}\n")
            log_handle.flush()
    else:
        def log_message(msg):
            pass  # Do nothing if no log file
    
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
            # Use adaptive chunking if enabled and no specific chunk size provided
            if adaptive_chunking and (chunk_size is None or chunk_overlap is None):
                optimal_chunk_size, optimal_chunk_overlap = get_optimal_chunk_settings(document_path)
                if chunk_size is None:
                    chunk_size = optimal_chunk_size
                if chunk_overlap is None:
                    chunk_overlap = optimal_chunk_overlap
                print(f"Using adaptive chunking settings: size={chunk_size}, overlap={chunk_overlap}")
            else:
                # Use default values if not specified
                if chunk_size is None:
                    chunk_size = 1000
                if chunk_overlap is None:
                    chunk_overlap = 100
            
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
                
                # Prepare arguments for each chunk
                chunk_args = [(chunk, i, len(chunks)) for i, chunk in enumerate(chunks)]
                
                # Set up progress tracking
                print(f"Processing {len(chunks)} chunks in parallel...\n")
                progress_tracker = ProgressTracker(len(chunks))
                
                # Create a list to hold all result data
                results = [None] * len(chunks)
                
                # Function to update progress when a chunk is completed
                def update_progress(future):
                    try:
                        idx, result = future.result(timeout=1200)  # Timeout after 20 minutes
                        if result:
                            # Store the result in the correct position
                            results[idx] = result
                            
                            # Log more details about successful extraction
                            entity_count = len(result.get("entities", []))
                            relationship_count = len(result.get("relationships", []))
                            if entity_count > 0 or relationship_count > 0:
                                log_message(f"Chunk {idx+1}/{len(chunks)}: Successfully extracted {entity_count} entities and {relationship_count} relationships")
                            else:
                                log_message(f"Chunk {idx+1}/{len(chunks)}: Extraction completed but no entities or relationships found")
                            
                        # Update progress display
                        progress_tracker.update(idx, result)
                        
                        # Log detailed info if verbose
                        if verbose and result:
                            entity_count = len(result.get("entities", []))
                            relationship_count = len(result.get("relationships", []))
                            log_message(f"Chunk {idx+1}/{len(chunks)}: Found {entity_count} entities and {relationship_count} relationships")
                    except concurrent.futures.TimeoutError:
                        log_message(f"Timeout while waiting for chunk result")
                    except Exception as e:
                        log_message(f"Error processing chunk: {e}")
                
                # Use ThreadPoolExecutor for parallel processing 
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                    # Submit all tasks and add callbacks
                    futures = []
                    # Only mark chunks as active when they're actually being processed
                    active_chunks = [False] * len(chunks)
                    
                    for i, arg in enumerate(chunk_args):
                        # Only mark the first max_workers chunks as active initially
                        if i < max_workers:
                            progress_tracker.mark_chunk_active(arg[1])  # arg[1] is the chunk index
                            active_chunks[i] = True
                            
                        future = executor.submit(process_chunk_wrapper, arg)
                        future.add_done_callback(update_progress)
                        futures.append(future)
                    
                    # Wait for futures with periodic hang checks
                    try:
                        completed_count = 0
                        remaining_futures = futures[:]
                        while remaining_futures:
                            # Wait for some futures to complete (with a timeout)
                            just_completed, remaining_futures = concurrent.futures.wait(
                                remaining_futures, 
                                timeout=30,  # Check every 30 seconds
                                return_when=concurrent.futures.FIRST_COMPLETED
                            )
                            
                            # For each completed future, activate a new chunk if there are any left
                            for _ in just_completed:
                                completed_count += 1
                                next_chunk_index = max_workers + completed_count - 1
                                if next_chunk_index < len(chunk_args):
                                    progress_tracker.mark_chunk_active(chunk_args[next_chunk_index][1])
                            
                            # Check for potentially hanging chunks with proper locking
                            with extraction_step_lock:
                                hung_chunks = progress_tracker.check_for_hangs()
                            
                            # If we've been running for too long, cancel everything
                            if time.time() - start_time > 86400:  # 24 hour global timeout
                                print("\nGlobal timeout reached! Cancelling remaining tasks...")
                                for future in remaining_futures:
                                    future.cancel()
                                break
                    except Exception as e:
                        print(f"\nError waiting for futures: {e}")
                        # Try to cancel any remaining tasks
                        for future in futures:
                            if not future.done():
                                future.cancel()
                    
                    # Collect all non-None results into all_extracted_data
                    progress_tracker.close()  # Close the progress tracker
                    all_extracted_data = [result for result in results if result is not None]
                    print(f"\nCollected {len(all_extracted_data)} valid results from parallel processing")

                    if not all_extracted_data:
                        print("\n⚠️ Warning: No valid data was extracted from any chunks in parallel mode.")
            # For sequential processing
            else:
                print("Using sequential processing")
                # Create a progress bar for sequential processing
                progress_bar = tqdm.tqdm(total=len(chunks), desc="Processing chunks")
                
                successful_chunks = 0
                total_entities = 0
                total_relationships = 0
                
                for i, chunk in enumerate(chunks):
                    log_message(f"Processing chunk {i+1}/{len(chunks)}...")
                    extracted_data = process_chunk(chunk, i, len(chunks))
                    
                    if extracted_data:
                        all_extracted_data.append(extracted_data)
                        entity_count = len(extracted_data.get("entities", []))
                        relationship_count = len(extracted_data.get("relationships", []))
                        total_entities += entity_count
                        total_relationships += relationship_count
                        successful_chunks += 1
                        
                        # Log detailed output if verbose
                        if verbose:
                            log_message(f"Chunk {i+1}/{len(chunks)}: Found {entity_count} entities and {relationship_count} relationships")
                    
                    # Update progress bar description with stats
                    progress_bar.set_description(
                        f"Processing chunks | Success: {successful_chunks}/{i+1} | "
                        f"Entities: {total_entities} | Relationships: {total_relationships}"
                    )
                    progress_bar.update(1)
                
                progress_bar.close()
                print(f"\nCompleted processing {successful_chunks}/{len(chunks)} chunks successfully")
            
            # Save extracted data if requested
            if save_data and all_extracted_data:
                save_extracted_data(all_extracted_data, output_file)
        
        if not merged_data.get('entities') and not merged_data.get('relationships'):
            print("\n⚠️ Error: No entities or relationships were found after merging extracted data.")
            print("Please check if your document contains the expected content or try adjusting chunking parameters.")
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
    finally:
        # Clean up any global resources
        with extraction_step_lock:
            extraction_steps.clear()
            
        # Close log file if it was opened
        if log_file and 'log_handle' in locals():
            log_handle.close()

# The if __name__ == "__main__" block
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Process documents and build a Neo4j knowledge graph")
    parser.add_argument("document_path", help="Path to the document to process")
    parser.add_argument("--chunk-size", type=int, default=None, help="Size of chunks to split document into")
    parser.add_argument("--chunk-overlap", type=int, default=None, help="Overlap between chunks")
    parser.add_argument("--preserve", action="store_true", help="Preserve existing data in Neo4j (don't clear)")
    parser.add_argument("--parallel", action="store_true", help="Process chunks in parallel")
    parser.add_argument("--workers", type=int, default=4, help="Number of worker threads for parallel processing")
    parser.add_argument("--quiet", action="store_true", help="Reduce verbosity of output")
    parser.add_argument("--verbose-extraction", action="store_true", help="Show detailed extraction steps for each chunk")
    parser.add_argument("--start-chunk", type=int, default=0, help="Start processing from this chunk index")
    parser.add_argument("--end-chunk", type=int, default=None, help="Stop processing at this chunk index")
    parser.add_argument("--save", action="store_true", help="Save extracted data to file for later use")
    parser.add_argument("--load", action="store_true", help="Load previously extracted data instead of processing again")
    parser.add_argument("--output-file", help="Path to save/load extracted data (default: based on document name)")
    parser.add_argument("--adaptive", action="store_true", help="Use adaptive chunk sizing based on document size")
    parser.add_argument("--log-file", help="Path to save detailed processing logs (optional)")
    parser.add_argument("--timeout", type=int, default=10800, help="Global timeout in seconds (default: 3600)")
    
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
    
    # If using adaptive chunking, pass None for chunk_size and chunk_overlap
    chunk_size = None if args.adaptive else args.chunk_size
    chunk_overlap = None if args.adaptive else args.chunk_overlap
    
    # Set up log file path if not provided
    # Default to not logging unless explicitly requested and permissions allowed
    log_file = None
    if args.log_file:
        try:
            # Only try to log if explicitly requested
            log_dir = os.path.dirname(args.log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            with open(args.log_file, 'w') as test:
                test.write("Testing log file permissions\n")
            log_file = args.log_file
        except (PermissionError, OSError) as e:
            print(f"⚠️ Warning: Cannot write to specified log file: {e}")
    
    try:
        process_document_to_graph(
            document_path=args.document_path,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            clear_existing=not args.preserve,
            parallel=args.parallel,
            max_workers=args.workers,
            verbose=not args.quiet,
            start_chunk=args.start_chunk,
            end_chunk=args.end_chunk,
            save_data=args.save,
            load_data=args.load,
            output_file=args.output_file,
            adaptive_chunking=args.adaptive,
            log_file=log_file,
            extraction_verbose=args.verbose_extraction
        )
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user. Cleaning up...")
        # Attempt to clean up any lingering threads
        for thread in threading.enumerate():
            if thread != threading.current_thread():
                print(f"Force terminating thread: {thread.name}")
                # We can't forcibly terminate threads in Python, but we can notify the user
        
        # Clear any global state
        with extraction_step_lock:
            extraction_steps.clear()
    
    total_time = time.time() - start_time
    print(f"\nTotal processing time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")

