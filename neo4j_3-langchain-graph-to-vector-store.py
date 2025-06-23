# graph_to_vector.py
import os
import argparse
from dotenv import load_dotenv
import warnings
from typing import List, Dict, Any, Tuple, Optional
import time

# LangChain imports
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_community.embeddings import OllamaEmbeddings
from langchain.schema import Document

# Load environment variables from .env file
load_dotenv()
warnings.filterwarnings("ignore")


def escape_property_name(prop_name):
    """Escape Neo4j property names that contain spaces or special characters."""
    if ' ' in prop_name or '-' in prop_name or any(c in prop_name for c in ',.;:?!@#$%^&*()+=[]{}'):
        return f"`{prop_name}`"
    return prop_name


def sanitize_param_name(param_name):
    """Convert parameter names with spaces or special characters to valid parameter names."""
    if ' ' in param_name or '-' in param_name or any(c in param_name for c in ',.;:?!@#$%^&*()+=[]{}'):
        # Replace spaces and special chars with underscores
        return ''.join(c if c.isalnum() else '_' for c in param_name)
    return param_name

def initialize_neo4j_connection() -> Optional[Neo4jGraph]:
    """Initialize and return a Neo4j graph connection.
    
    Returns:
        Neo4jGraph or None: Connected Neo4j graph object or None if connection fails
    """
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
        return None


def initialize_embeddings(model_name: str = "nomic-embed-text:latest") -> OllamaEmbeddings:
    """Initialize and return embedding model.
    
    This function creates an embedding model client that converts text to vector embeddings.
    It does NOT use Ollama for text generation (LLM functionality).
    
    Understanding embeddings vs LLMs:
    - Embeddings (what we need here): Convert text into numerical vectors that represent semantic meaning
      These vectors typically have 768-1536 dimensions and are used for similarity search
    - LLMs: Generate new text responses based on prompts
    
    For RAG applications, we use:
    1. Embeddings to convert documents to vectors and find similar documents 
    2. LLMs to generate responses based on the retrieved documents
    
    Args:
        model_name: Name of the embedding model in Ollama
                   Recommended models for embeddings: "nomic-embed-text:latest", "all-minilm"
                   
    Returns:
        OllamaEmbeddings: The embedding model client
    """
    print(f"Initializing Ollama embeddings with model: {model_name}")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    try:
        embeddings = OllamaEmbeddings(
            model=model_name,
            base_url=base_url
        )
        # Test embeddings
        test_embedding = embeddings.embed_query("Test embedding")
        print(f"✓ Successfully connected to Ollama (embedding dimension: {len(test_embedding)})")
        print(f"  Note: Embedding dimension is {len(test_embedding)}. This is the 'size' of the vector that represents text.")
        return embeddings
    except Exception as e:
        print(f"❌ Failed to connect to Ollama: {e}")
        print(f"  Please ensure Ollama is running at {base_url} and model '{model_name}' is available.")
        print(f"  You can install the model with: ollama pull {model_name}")
        raise


def get_available_node_labels(graph: Neo4jGraph) -> List[str]:
    """Get all available node labels in the graph."""
    try:
        result = graph.query("""
        CALL db.labels() YIELD label
        RETURN label
        """)
        labels = [record["label"] for record in result]
        return labels
    except Exception as e:
        print(f"❌ Error retrieving node labels: {e}")
        return []


def get_node_properties(graph: Neo4jGraph, label: str) -> List[str]:
    """Get all properties for a specific node label."""
    try:
        result = graph.query(f"""
        MATCH (n:{label})
        WHERE n IS NOT NULL
        WITH n LIMIT 1
        RETURN keys(n) AS properties
        """)
        
        if not result:
            return []
        
        return result[0]["properties"]
    except Exception as e:
        print(f"❌ Error retrieving properties for {label} nodes: {e}")
        return []


def get_node_count(graph: Neo4jGraph, label: str, text_property: Optional[str] = None) -> int:
    """Get the count of nodes with the given label, optionally with non-null text property."""
    try:
        query = f"MATCH (n:{label})"
        if text_property:
            query += f" WHERE n.{text_property} IS NOT NULL"
        query += " RETURN count(n) AS count"
        
        result = graph.query(query)
        return result[0]["count"] if result else 0
    except Exception as e:
        print(f"❌ Error getting node count: {e}")
        return 0


def identify_text_properties(properties: List[str]) -> List[str]:
    """Identify potential text content properties based on property names."""
    text_properties = []
    potential_text_fields = [
        "text", "content", "description", "body", "abstract", 
        "summary", "information", "details", "data", "title",
        "name", "message", "comment", "review", "bio", "about"
    ]
    
    # First pass: look for exact matches in preferred order
    priority_fields = ["description", "text", "content", "body", "name", "title"]
    for field in priority_fields:
        if field in properties:
            text_properties.append(field)
    
    # Second pass: check for partial matches if we haven't found any exact matches
    if not text_properties:
        for prop in properties:
            prop_lower = prop.lower()
            # Check if the property name contains any of the potential text fields
            if any(text_field in prop_lower for text_field in potential_text_fields):
                text_properties.append(prop)
    
    return text_properties


def extract_text_content_batch(
    graph: Neo4jGraph, 
    label: str, 
    text_property: str, 
    filter_cypher: Optional[str] = None,
    batch_size: int = 500,
    skip: int = 0
) -> List[Dict[str, Any]]:
    """Extract text content from the graph in batches."""
    # Build the query with optional filter
    query_base = f"""
    MATCH (n:{label})
    WHERE n.{text_property} IS NOT NULL
    """
    
    if filter_cypher:
        query_base += f" AND {filter_cypher}"
    
    # Update to use elementId instead of id() function
    query = query_base + f"""
    RETURN elementId(n) AS internal_id, n AS node_properties
    SKIP {skip} LIMIT {batch_size}
    """
    
    try:
        result = graph.query(query)
        return result
    except Exception as e:
        print(f"❌ Error extracting text content: {e}")
        return []


def create_documents_from_nodes(nodes_data: List[Dict[str, Any]], text_property: str) -> List[Document]:
    """Create documents for vectorization from node data."""
    documents = []
    complex_metadata_count = 0
    
    for item in nodes_data:
        node_props = item["node_properties"]
        
        # Skip if text content is missing
        if text_property not in node_props or not node_props[text_property]:
            continue
            
        # Create metadata - include all properties except the text content
        # Handle complex data types (lists, dicts) by converting them to strings
        metadata = {}
        for k, v in node_props.items():
            if k != text_property:
                if isinstance(v, (list, dict)):
                    # Convert complex types to string representation
                    try:
                        metadata[k] = str(v)
                        complex_metadata_count += 1
                    except:
                        # If conversion fails, skip this metadata
                        pass
                elif v is not None:
                    metadata[k] = v
        
        # Add internal ID to metadata
        metadata["internal_id"] = item["internal_id"]
        
        # Create document with content and metadata
        try:
            # Convert any non-string content to string
            content = str(node_props[text_property])
            
            doc = Document(
                page_content=content,
                metadata=metadata
            )
            documents.append(doc)
        except Exception as e:
            print(f"⚠️ Warning: Could not create document from node {item['internal_id']}: {e}")
    
    if complex_metadata_count > 0:
        print(f"  Note: Converted {complex_metadata_count} complex metadata values (lists/dicts) to strings")
    
    return documents

def create_vector_store_manual(
    documents: List[Document],
    embeddings: OllamaEmbeddings,
    label: str,
    text_property: str
) -> Tuple[Any, str]:
    """Create a vector store manually using direct Neo4j queries.
    
    This function is optimized for Neo4j 5.22.0.
    """
    from neo4j import GraphDatabase
    
    # Generate a consistent index name based on node label and text property
    index_name = f"{label.lower()}_{text_property.lower()}"
    
    # Initialize Neo4j connection
    url = ("bolt://localhost:7687")
    username = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")
    
    try:
        driver = GraphDatabase.driver(url, auth=(username, password))
        
        # Check if we have any documents with metadata
        if documents and hasattr(documents[0], 'metadata') and documents[0].metadata:
            print(f"  Available metadata keys: {list(documents[0].metadata.keys())}")
        
        print(f"  Creating vector index: {index_name}")
        
        # Step 1: Check if vector index exists
        with driver.session() as session:
            # Check Neo4j version first
            version_query = "CALL dbms.components() YIELD name, versions RETURN versions[0] as version"
            try:
                version_result = session.run(version_query).single()
                neo4j_version = version_result["version"] if version_result else "unknown"
                print(f"  Detected Neo4j version: {neo4j_version}")
            except Exception as e:
                print(f"  Could not determine Neo4j version, assuming 5.22.0: {e}")
                neo4j_version = "5.22.0"
            
            # Check if vector index exists
            index_query = """
            SHOW VECTOR INDEXES
            YIELD name
            WHERE name = $index_name
            RETURN count(*) as count
            """    
            try:
                result = session.run(index_query, index_name=index_name).single()
                index_exists = result and result["count"] > 0
            except Exception as e:
                print(f"  Error checking for vector index, will attempt to create: {e}")
                index_exists = False
            

            if not index_exists:
                # Create vector index
                test_embedding = embeddings.embed_query("Test")
                if not test_embedding or len(test_embedding) == 0:
                    print(f"  ❌ Error: Embedding model returned empty vector")
                    return None, None
                    
                dimension = len(test_embedding)
                create_index_query = """
                CALL db.index.vector.createNodeIndex(
                $index_name,
                $label,
                $property,
                $dimension,
                'cosine'
                )
                """
                try:
                    session.run(
                        create_index_query, 
                        index_name=index_name,
                        label=label,
                        property="embedding",
                        dimension=dimension
                    )
                    print(f"  ✓ Created new vector index: {index_name}")
                except Exception as e:
                    print(f"  ⚠️ Error creating vector index: {e}")
                    print(f"  Will continue with existing index if available")
            else:
                print(f"  ✓ Vector index already exists: {index_name}")
        
        # Step 2: Check for constraints
        with driver.session() as session:
            unique_props = []
            
            try:
                # Neo4j 5.22.0 has a simpler constraint query
                constraint_query = """
                SHOW CONSTRAINTS
                """
                constraints = list(session.run(constraint_query))
                
                # Process constraints to find uniqueness constraints for our label
                for constraint in constraints:
                    # Get constraint type and check if it's for uniqueness
                    constraint_type = constraint.get("type", "")
                    if "UNIQUENESS" in constraint_type:
                        # Check if this constraint is for our label
                        labels_or_types = constraint.get("labelsOrTypes", [])
                        if isinstance(labels_or_types, list) and label in labels_or_types:
                            # Get properties covered by this constraint
                            properties = constraint.get("properties", [])
                            if isinstance(properties, list):
                                unique_props.extend(properties)
                            else:
                                unique_props.append(str(properties))
                        elif isinstance(labels_or_types, str) and label == labels_or_types:
                            # Handle case where labelsOrTypes might be a string
                            properties = constraint.get("properties", [])
                            if isinstance(properties, list):
                                unique_props.extend(properties)
                            else:
                                unique_props.append(str(properties))
            except Exception as e:
                print(f"  Warning: Error checking constraints: {e}")
                # Continue without constraint information
            
            if unique_props:
                print(f"  Found uniqueness constraints on properties: {unique_props}")
                
        # Step 3: Process documents in batches
        batch_size = 100
        total_docs = len(documents)
        print(f"  Processing {total_docs} documents in batches of {batch_size}")
        
        # Process documents in batches
        for i in range(0, total_docs, batch_size):
            batch = documents[i:i+batch_size]
            print(f"  Processing batch {i//batch_size + 1}/{(total_docs+batch_size-1)//batch_size}...")
            
            # Generate embeddings for this batch
            texts = [doc.page_content for doc in batch]
            vectors = embeddings.embed_documents(texts)
            
            # Insert documents with their embeddings
            with driver.session() as session:
                # Insert or update in a single transaction for atomicity
                with session.begin_transaction() as tx:
                    for j, (doc, vector) in enumerate(zip(batch, vectors)):
                        metadata = {k: v for k, v in doc.metadata.items() if v is not None}
                        
                        # First check if the node exists
                        if "internal_id" in metadata:
                            # Find by internal_id
                            match_query = f"""
                            MATCH (n:{label})
                            WHERE elementId(n) = $internal_id
                            RETURN n
                            """
                            result = tx.run(match_query, internal_id=metadata.get("internal_id")).single()
                            
                            if result:
                                # Node exists, update it
                                update_query = f"""
                                MATCH (n:{label})
                                WHERE elementId(n) = $internal_id
                                SET n.{text_property} = $text_content
                                """
                                
                                # Add metadata properties
                                param_mapping = {}  # To store mapping from original keys to sanitized param names
                                for key in metadata:
                                    if key != "internal_id":  # Already used in WHERE clause
                                        escaped_key = escape_property_name(key)
                                        param_key = sanitize_param_name(key)
                                        param_mapping[key] = param_key
                                        update_query += f", n.{escaped_key} = ${param_key}"
                                
                                # Execute update query
                                params = {"internal_id": metadata.get("internal_id"), "text_content": doc.page_content}
                                # Add sanitized parameter names
                                for original_key, param_key in param_mapping.items():
                                    params[param_key] = metadata.get(original_key)
                            else:
                                # Node doesn't exist, create it
                                create_query = f"""
                                CREATE (n:{label} {{internal_id: $internal_id, {text_property}: $text_content}}
                                """
                                
                                # Add metadata properties
                                create_query = create_query[:-1] + ", "  # Remove closing brace and add comma
                                param_mapping = {}  # To store mapping from original keys to sanitized param names
                                for key in metadata:
                                    if key != "internal_id":  # Already included above
                                        escaped_key = escape_property_name(key)
                                        param_key = sanitize_param_name(key)
                                        param_mapping[key] = param_key
                                        create_query += f"{escaped_key}: ${param_key}, "
                                
                                # Remove trailing comma and close the brackets
                                create_query = create_query[:-2] + "})"
                                
                                # Execute create query
                                params = {"internal_id": metadata.get("internal_id"), "text_content": doc.page_content}
                                # Add sanitized parameter names
                                for original_key, param_key in param_mapping.items():
                                    params[param_key] = metadata.get(original_key)
                        else:
                            # No internal_id, check for other unique properties
                            # If there are uniqueness constraints, we need to handle them
                            if unique_props and any(prop in metadata for prop in unique_props):
                                # Build a WHERE clause for all unique properties available in metadata
                                where_clauses = []
                                param_mapping = {}  # To store mapping from original keys to sanitized param names
                                for prop in unique_props:
                                    if prop in metadata:
                                        escaped_prop = escape_property_name(prop)
                                        param_prop = sanitize_param_name(prop)
                                        param_mapping[prop] = param_key = param_prop
                                        where_clauses.append(f"n.{escaped_prop} = ${param_key}")
                                
                                if where_clauses:
                                    where_str = " OR ".join(where_clauses)
                                    match_query = f"""
                                    MATCH (n:{label})
                                    WHERE {where_str}
                                    RETURN n
                                    """
                                    
                                    # Create parameters dictionary with sanitized keys
                                    query_params = {}
                                    for original_key, param_key in param_mapping.items():
                                        if original_key in unique_props:
                                            query_params[param_key] = metadata.get(original_key)
                                    
                                    result = tx.run(match_query, **query_params).single()
                                    
                                    if result:
                                        # Node exists, update it
                                        update_query = f"""
                                        MATCH (n:{label})
                                        WHERE {where_str}
                                        SET n.{text_property} = $text_content
                                        """

                                        # Add metadata properties
                                        param_mapping = {}  # To store mapping from original keys to sanitized param names
                                        for key in metadata:
                                            if key not in unique_props:  # Don't update unique properties
                                                escaped_key = escape_property_name(key)
                                                param_key = sanitize_param_name(key)
                                                param_mapping[key] = param_key
                                                update_query += f", n.{escaped_key} = ${param_key}"

                                        # Execute update query
                                        params = {"text_content": doc.page_content}

                                        # Add sanitized parameters for both metadata and WHERE clause
                                        for original_key, param_key in param_mapping.items():
                                            params[param_key] = metadata.get(original_key)

                                        # Also add sanitized parameters for unique properties in WHERE clause
                                        for prop in unique_props:
                                            if prop in metadata:
                                                param_prop = sanitize_param_name(prop)
                                                params[param_prop] = metadata.get(prop)

                                        # Execute the query with the properly prepared parameters
                                        tx.run(update_query, params)
                                        continue
                            
                            # If we reach here, either there are no unique constraints or the node doesn't exist
                            # Create a new node
                            create_query = f"""
                            CREATE (n:{label} {{{text_property}: $text_content}}
                            """

                            # Add metadata properties
                            create_query = create_query[:-1] + ", "  # Remove closing brace and add comma
                            param_mapping = {}  # To store mapping from original keys to sanitized param names
                            for key in metadata:
                                escaped_key = escape_property_name(key)
                                param_key = sanitize_param_name(key)
                                param_mapping[key] = param_key
                                create_query += f"{escaped_key}: ${param_key}, "

                            # Remove trailing comma and close the brackets
                            create_query = create_query[:-2] + "})"

                            # Execute create query
                            params = {"text_content": doc.page_content}
                            # Add sanitized parameter names
                            for original_key, param_key in param_mapping.items():
                                params[param_key] = metadata.get(original_key)
                            tx.run(create_query, params)
                        
                        # Set vector property - using correct Neo4j 5.22.0 syntax
                        # Note: This procedure doesn't yield values in Neo4j 5.22.0
                        if "internal_id" in metadata:
                            vector_query = f"""
                            MATCH (n:{label})
                            WHERE elementId(n) = $internal_id
                            CALL db.create.setNodeVectorProperty(n, 'embedding', $embedding)
                            """
                            tx.run(vector_query, internal_id=metadata.get("internal_id"), embedding=vector)
                        else:
                            # Find by text content and metadata
                            conditions = []
                            param_mapping = {}  # To store mapping from original keys to sanitized param names
                            for key, value in metadata.items():
                                if value is not None:
                                    escaped_key = escape_property_name(key)
                                    param_key = sanitize_param_name(key)
                                    param_mapping[key] = param_key
                                    conditions.append(f"n.{escaped_key} = ${param_key}")

                            where_clause = f"n.{text_property} = $text_content"
                            if conditions:
                                where_clause += " AND " + " AND ".join(conditions)
                                
                            vector_query = f"""
                            MATCH (n:{label})
                            WHERE {where_clause}
                            CALL db.create.setNodeVectorProperty(n, 'embedding', $embedding)
                            """
                            params = {"text_content": doc.page_content, "embedding": vector}
                            # Add sanitized parameter names
                            for original_key, param_key in param_mapping.items():
                                params[param_key] = metadata.get(original_key)
            
            print(f"  ✓ Processed {min(i+batch_size, total_docs)}/{total_docs} documents")
        
        print(f"✓ Successfully created vector store for {label} nodes")
        
        # Create a simple wrapper object that mimics basic Neo4jVector functionality
        class SimpleVectorStore:
            def __init__(self, driver, index_name, label, embedding_property):
                self.driver = driver
                self.index_name = index_name
                self.label = label
                self.embedding_property = embedding_property
                
            def similarity_search(self, query, k=3):
                # Convert query to embedding
                query_embedding = embeddings.embed_query(query)
                
                # Perform vector search
                with self.driver.session() as session:
                    search_query = f"""
                    CALL db.index.vector.queryNodes($index_name, $k, $embedding)
                    YIELD node, score
                    RETURN node, score
                    """
                    result = session.run(
                        search_query, 
                        index_name=self.index_name,
                        k=k,
                        embedding=query_embedding
                    )
                    
                    # Convert results to Document objects
                    docs = []
                    for record in result:
                        node = record["node"]
                        node_props = dict(node)
                        
                        # Create metadata without the text content
                        metadata = {k: v for k, v in node_props.items() 
                                 if k != text_property and v is not None}
                        
                        # Create Document
                        doc = Document(
                            page_content=node_props.get(text_property, ""),
                            metadata=metadata
                        )
                        docs.append(doc)
                    
                    return docs
        
        # Create and return the vector store wrapper
        vector_store = SimpleVectorStore(driver, index_name, label, "embedding")
        return vector_store, index_name
        
    except Exception as e:
        print(f"❌ Error creating vector store: {e}")
        print(f"  This may be due to compatibility issues with Neo4j version or configuration")
        if "constraint" in str(e).lower():
            print(f"  This error appears to be related to database constraints")
            print(f"  You can check Neo4j constraints with: SHOW CONSTRAINTS")
        raise

def create_vector_store(
    documents: List[Document], 
    embeddings: OllamaEmbeddings, 
    label: str, 
    text_property: str
) -> Tuple[Any, str]:
    """Create a Neo4j vector store from documents.
    
    This function now skips the LangChain attempt and goes directly to the manual implementation,
    which has better version compatibility.
    """
    # Generate a consistent index name based on node label and text property
    index_name = f"{label.lower()}_{text_property.lower()}"
    
    # Skip LangChain Neo4jVector since it has compatibility issues
    # Go straight to our manual implementation
    print("  Using manual Neo4j vector store implementation for better version compatibility...")
    return create_vector_store_manual(documents, embeddings, label, text_property)


def process_node_type_in_batches(
    graph: Neo4jGraph, 
    embeddings: OllamaEmbeddings, 
    label: str, 
    text_property: Optional[str] = None, 
    filter_cypher: Optional[str] = None,
    batch_size: int = 500
) -> Tuple[Optional[Any], Optional[str]]:
    """Process a specific node type in batches and create a vector store for it."""
    print(f"\n{'='*60}")
    print(f"PROCESSING NODE TYPE: {label}")
    print(f"{'='*60}")
    
    # Step 1: If no text property provided, identify potential text properties
    if not text_property:
        properties = get_node_properties(graph, label)
        text_properties = identify_text_properties(properties)
        
        if not text_properties:
            print(f"❌ No suitable text properties found for {label} nodes. Available properties: {properties}")
            return None, None
        
        # Use the first identified text property
        text_property = text_properties[0]
        print(f"✓ Automatically selected text property: {text_property}")
        print(f"  (Other potential text properties: {text_properties[1:] if len(text_properties) > 1 else 'None'})")
    
    # Step 2: Count nodes to process
    total_nodes = get_node_count(graph, label, text_property)
    if total_nodes == 0:
        print(f"❌ No {label} nodes found with non-empty {text_property} property.")
        return None, None
    
    print(f"\nFound {total_nodes} {label} nodes with {text_property} property to process")
    if filter_cypher:
        print(f"Applying filter: {filter_cypher}")
    
    # Step 3: Process in batches
    all_documents = []
    processed = 0
    batch_num = 1
    start_time = time.time()
    
    while processed < total_nodes:
        print(f"\nProcessing batch {batch_num} (nodes {processed+1}-{min(processed+batch_size, total_nodes)} of {total_nodes})...")
        
        # Extract text content for this batch
        nodes_data = extract_text_content_batch(
            graph, label, text_property, filter_cypher, 
            batch_size=batch_size, skip=processed
        )
        
        if not nodes_data:
            print(f"⚠️ Warning: No data returned for batch {batch_num}")
            processed += batch_size
            batch_num += 1
            continue
        
        # Create documents for this batch
        batch_documents = create_documents_from_nodes(nodes_data, text_property)
        all_documents.extend(batch_documents)
        
        print(f"✓ Processed {len(batch_documents)} documents in batch {batch_num}")
        
        processed += len(nodes_data)
        batch_num += 1
        
        # Calculate and display progress
        progress = min(processed, total_nodes) / total_nodes * 100
        elapsed = time.time() - start_time
        docs_per_sec = processed / elapsed if elapsed > 0 else 0
        
        print(f"  Progress: {progress:.1f}% ({min(processed, total_nodes)}/{total_nodes}) - {docs_per_sec:.1f} nodes/sec")
    
    if not all_documents:
        print(f"❌ No valid documents created from {label} nodes.")
        return None, None
    
    print(f"\n✓ Total documents created: {len(all_documents)}")
    
    # Print a sample document to verify content and metadata
    if all_documents:
        print("\nSample document:")
        sample = all_documents[0]
        print(f"  Content (first 100 chars): {sample.page_content[:100]}...")
        print(f"  Metadata keys: {list(sample.metadata.keys())}")
    
    # Step 4: Create vector store
    print(f"\nCreating vector store for {label} nodes...")
    vector_store, index_name = create_vector_store(all_documents, embeddings, label, text_property)
    
    print(f"✓ Vector store created in Neo4j with index name: {index_name}")
    print(f"  Total processing time: {time.time() - start_time:.1f} seconds")
    
    return vector_store, index_name

def test_vector_search(vector_store: Any, query: str, k: int = 3) -> Optional[List[Document]]:
    """Test vector search with a sample query."""
    print(f"\nTesting vector search with query: '{query}'")
    try:
        docs = vector_store.similarity_search(query, k=k)
        
        print(f"\nSearch results ({len(docs)} documents):")
        for i, doc in enumerate(docs):
            print(f"\nResult {i+1}:")
            # Print some useful metadata
            for key, value in doc.metadata.items():
                if key in ['id', 'name', 'title', 'internal_id']:
                    print(f"  {key}: {value}")
            
            # Print content snippet
            print(f"  Content snippet: {doc.page_content[:150]}...")
            print(f"  Similarity: Semantic match")
            
        return docs
    except Exception as e:
        print(f"❌ Error during vector search: {e}")
        if "No such index" in str(e):
            print(f"  The index doesn't exist or hasn't been properly created.")
            print(f"  Check that the vector index was successfully created in Neo4j.")
        elif "Invalid input" in str(e):
            print(f"  There may be a syntax issue with the Neo4j query.")
            print(f"  This could be due to version incompatibility.")
        return None


def main():
    parser = argparse.ArgumentParser(description="Create vector stores from Neo4j graph nodes")
    
    # Basic options
    parser.add_argument("--label", help="Node label to process")
    parser.add_argument("--text-property", help="Property containing text content")
    parser.add_argument("--filter", help="Additional Cypher filter condition")
    
    # Model options
    parser.add_argument("--model", default="nomic-embed-text:latest", 
                        help="Ollama embedding model to use (default: nomic-embed-text:latest)")
    
    # Discovery options
    parser.add_argument("--list-labels", action="store_true", help="List all available node labels")
    parser.add_argument("--all", action="store_true", help="Process all node labels")
    
    # Processing options
    parser.add_argument("--batch-size", type=int, default=500, 
                        help="Number of nodes to process in each batch")
    
    # Testing options
    parser.add_argument("--test-query", help="Test query for the created vector store(s)")
    parser.add_argument("--k", type=int, default=3, 
                        help="Number of results to return in test query")
    
    # Help commands
    parser.add_argument("--explain-rag", action="store_true", 
                        help="Print explanation about RAG and how this tool helps")
    parser.add_argument("--list-embedding-models", action="store_true",
                        help="List recommended embedding models for Ollama")
    
    args = parser.parse_args()
    
    # Initialize Neo4j connection
    graph = initialize_neo4j_connection()
    if not graph:
        return
    
    # Handle help commands
    if args.explain_rag:
        print("\n" + "="*60)
        print("RETRIEVAL AUGMENTED GENERATION (RAG) EXPLANATION")
        print("="*60)
        print("\nRAG is a technique that enhances LLMs with external knowledge from a vector database.")
        print("\nThe process works in 3 main steps:")
        print("1. INDEXING (what this script does):")
        print("   - Extract text from source (in this case Neo4j nodes)")
        print("   - Convert text to embeddings (vector representations)")
        print("   - Store embeddings in a vector database (Neo4j in this case)")
        print("\n2. RETRIEVAL (when querying):")
        print("   - Convert user query to an embedding")
        print("   - Find most similar documents in the vector database")
        print("   - Retrieve relevant information")
        print("\n3. GENERATION:")
        print("   - Send retrieved information + user query to an LLM")
        print("   - LLM generates a response based on both")
        print("\nThis script handles step 1 (Indexing) by:")
        print("   - Finding text content in Neo4j nodes")
        print("   - Converting it to embeddings using Ollama")
        print("   - Storing both text and embeddings back in Neo4j")
        print("\nHybrid RAG adds traditional keyword search to improve retrieval accuracy.")
        return
        
    if args.list_embedding_models:
        print("\n" + "="*60)
        print("RECOMMENDED EMBEDDING MODELS FOR OLLAMA")
        print("="*60)
        print("\nText embedding models convert text to vectors. Here are recommended models:")
        print("\n1. nomic-embed-text:latest (default, recommended)")
        print("   - Dimension: 768")
        print("   - Good balance of quality and performance")
        print("   - Install: ollama pull nomic-embed-text:latest")
        print("\n2. all-minilm")
        print("   - Dimension: 384")
        print("   - Faster, smaller, but less precise")
        print("   - Install: ollama pull all-minilm")
        print("\n3. mxbai-embed-large")
        print("   - Dimension: 1024")
        print("   - Higher quality, but more resource-intensive")
        print("   - Install: ollama pull mxbai-embed-large")
        print("\nEmbedding dimension refers to how many numbers are used to represent each text fragment.")
        print("Higher dimensions typically provide better accuracy at the cost of more storage and processing time.")
        return
    
    # List all available labels if requested
    if args.list_labels:
        labels = get_available_node_labels(graph)
        if not labels:
            print("\n❌ No node labels found in the database.")
            return
            
        print("\nAvailable node labels in the Neo4j database:")
        for label in labels:
            properties = get_node_properties(graph, label)
            text_properties = identify_text_properties(properties)
            count = get_node_count(graph, label)
            print(f"  - {label} ({count} nodes)")
            print(f"    Properties: {properties}")
            print(f"    Potential text properties: {text_properties}")
        return
    
    # Initialize embeddings
    try:
        embeddings = initialize_embeddings(model_name=args.model)
    except Exception:
        return
    
    # Process nodes and create vector stores
    vector_stores = {}
    
    if args.all:
        # Process all available labels
        labels = get_available_node_labels(graph)
        if not labels:
            print("\n❌ No node labels found in the database.")
            return
            
        print(f"\nProcessing all {len(labels)} node labels...")
        
        for label in labels:
            vector_store, index_name = process_node_type_in_batches(
                graph, embeddings, label, args.text_property, args.filter,
                batch_size=args.batch_size
            )
            if vector_store and index_name:
                vector_stores[index_name] = vector_store
    
    elif args.label:
        # Process specific label
        vector_store, index_name = process_node_type_in_batches(
            graph, embeddings, args.label, args.text_property, args.filter,
            batch_size=args.batch_size
        )
        if vector_store and index_name:
            vector_stores[index_name] = vector_store
    
    else:
        print("\n❌ No node label specified. Use --label to specify a node label or --all to process all labels.")
        print("   Use --list-labels to see available node labels.")
        return
    
    # Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY: Created {len(vector_stores)} vector stores")
    for index_name in vector_stores:
        print(f"  - {index_name}")
    
    # Test query if provided
    if args.test_query and vector_stores:
        print(f"\n{'='*60}")
        print(f"TESTING VECTOR SEARCH")
        print(f"{'='*60}")
        
        for index_name, vector_store in vector_stores.items():
            print(f"\nTesting index: {index_name}")
            test_vector_search(vector_store, args.test_query, args.k)


if __name__ == "__main__":
    main()