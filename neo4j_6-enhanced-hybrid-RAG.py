# neo4j_6-enhanced-hybrid-RAG.py
import os
import argparse
from dotenv import load_dotenv
import warnings
from typing import List, Dict, Any, Optional
import time

# LangChain imports
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain.schema import Document
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain.chains.llm import LLMChain

# Load environment variables from .env file
load_dotenv()
warnings.filterwarnings("ignore")

# Global verbose flag
VERBOSE = False

def initialize_neo4j_connection():
    """Initialize and return a Neo4j graph connection."""
    # Print versions for debugging
    try:
        import langchain
        import langchain_community
        import neo4j
        print(f"Using langchain: {langchain.__version__}, langchain-community: {langchain_community.__version__}, neo4j: {neo4j.__version__}")
    except (ImportError, AttributeError) as e:
        print(f"Could not determine package versions: {e}")
    
    graph = Neo4jGraph(
        url=("bolt://localhost:7687"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD")
    )
    return graph

def initialize_embeddings(model_name="nomic-embed-text:latest"):
    """Initialize and return embedding model."""
    # List of models to try in order of preference
    models_to_try = [
        model_name,  # Try the specified model first
        "nomic-embed-text:latest",  # Good embedding model
        "all-minilm:latest",        # Smaller alternative
        "llama3:latest",            # LLM that can also do embeddings
        "gemma3:latest"             # Another option
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
            print(f"Attempting to use embedding model: {model}")
            embeddings = OllamaEmbeddings(
                model=model,
                base_url=base_url
            )
            
            # Test the embeddings with a simple query
            test_embedding = embeddings.embed_query("test embedding")
            print(f"✓ Successfully connected to Ollama using model: {model}")
            print(f"  Embedding dimension: {len(test_embedding)}")
            return embeddings
        except Exception as e:
            print(f"❌ Failed to use model {model}: {e}")
            last_exception = e
    
    # If we get here, all models failed
    raise ValueError(f"All embedding models failed. Last error: {last_exception}")

def initialize_llm(model_name="llama3.1:latest", temperature=0.1):
    """Initialize and return the LLM."""
    # List of models to try in order of preference
    models_to_try = [
        model_name,        # Try the specified model first
        "llama3-chatqa:8b",      # Good QA model
        "gemma3:4b",   # Another alternative
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

def get_available_vector_indices(graph):
    """Get all available vector indices in Neo4j."""
    try:
        # Neo4j 5.22.0 syntax
        result = graph.query("""
        SHOW INDEXES
        WHERE type = 'VECTOR'
        """)
        return [record["name"] for record in result]
    except Exception as e:
        try:
            # Alternative approach - get all indexes and filter
            result = graph.query("SHOW INDEXES")
            return [record["name"] for record in result if record.get("type") == "VECTOR"]
        except Exception as e2:
            print(f"❌ Error querying vector indices: {e2}")
            return []

def load_vector_store(graph, embeddings, index_name):
    """Load an existing vector store by index name."""
    # Try to infer node label and text property from index name
    # This is a common naming convention: label_property (e.g., person_name)
    if "_" in index_name:
        parts = index_name.split("_", 1)
        node_label = parts[0]
        text_property = parts[1]
    else:
        # Default values if we can't infer from name
        node_label = "Document"
        text_property = "text"
    
    # Default embedding property
    embedding_property = "embedding"
    
    # Try to get more information from the database if possible
    try:
        # Neo4j 5.22.0 syntax
        index_info = graph.query(f"""
        SHOW INDEXES
        WHERE name = '{index_name}'
        """)
        
        if index_info:
            index_record = index_info[0]
            
            # Extract label if available
            labels_or_types = index_record.get("labelsOrTypes", [])
            if isinstance(labels_or_types, list) and labels_or_types:
                node_label = labels_or_types[0]
            elif isinstance(labels_or_types, str):
                node_label = labels_or_types
            
            # Extract properties if available
            properties = index_record.get("properties", [])
            if isinstance(properties, list) and properties:
                # In Neo4j 5.22.0, typically the first property is the text property
                # and the second is the embedding
                if len(properties) >= 1 and not text_property:
                    text_property = properties[0]
                if len(properties) >= 2:
                    embedding_property = properties[1]
    except Exception as e:
        # If we can't get details, just use what we inferred from the name
        print(f"Note: Couldn't get detailed index information: {e}")
        print(f"Using parameters inferred from index name")
    
    print(f"✓ Loading vector store for index '{index_name}':")
    print(f"  - Node label: {node_label}")
    print(f"  - Text property: {text_property}")
    print(f"  - Embedding property: {embedding_property}")
    
    # Initialize Neo4j Vector store with existing index
    try:
        # Create a manual implementation similar to the one in neo4j_3-langchain-graph-to-vector-store.py
        from neo4j import GraphDatabase
        
        # Connect to Neo4j directly
        url = "bolt://localhost:7687"
        username = os.getenv("NEO4J_USERNAME")
        password = os.getenv("NEO4J_PASSWORD")
        
        # Simple class that mimics Neo4jVector basic functionality
        class CustomNeo4jVector:
            def __init__(self, embeddings, url, username, password, index_name, node_label, 
                         text_node_property, embedding_node_property):
                self.embeddings = embeddings
                self.url = url
                self.username = username
                self.password = password
                self.driver = GraphDatabase.driver(url, auth=(username, password))
                self.index_name = index_name
                self.node_label = node_label
                self.text_property = text_node_property
                self.embedding_property = embedding_node_property
            
            def similarity_search(self, query, k=3):
                # Convert query to embedding
                query_embedding = self.embeddings.embed_query(query)
                
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
                                 if k != self.text_property and v is not None}
                        
                        # Create Document
                        doc = Document(
                            page_content=node_props.get(self.text_property, ""),
                            metadata=metadata
                        )
                        docs.append(doc)
                    
                    return docs
        
        # Create our custom implementation
        vector_store = CustomNeo4jVector(
            embeddings=embeddings,
            url=url,
            username=username,
            password=password,
            index_name=index_name,
            node_label=node_label,
            text_node_property=text_property,
            embedding_node_property=embedding_property
        )
        
        # Test the implementation with a simple query
        test_docs = vector_store.similarity_search("test", k=1)
        print(f"  ✓ Successfully tested vector store (found {len(test_docs)} results for test query)")
        
        return vector_store
    except Exception as e:
        print(f"❌ Error creating custom vector store: {e}")
        print("  Attempting to use the official Neo4jVector implementations...")
        
        # Try multiple possible initialization parameter combinations
        try_methods = [
            # Try method 1: Using LangChain Neo4j native API (langchain-neo4j 0.4.0)
            lambda: Neo4jVector.from_existing_index(
                embedding=embeddings,
                url="bolt://localhost:7687",
                username=os.getenv("NEO4J_USERNAME"),
                password=os.getenv("NEO4J_PASSWORD"),
                index_name=index_name,
                node_label=node_label,
                text_node_property=text_property,
                embedding_node_property=embedding_property
            ),
            # Try method 2: Using 'embedding'
            lambda: Neo4jVector(
                embedding=embeddings,
                url="bolt://localhost:7687",
                username=os.getenv("NEO4J_USERNAME"),
                password=os.getenv("NEO4J_PASSWORD"),
                index_name=index_name,
                node_label=node_label,
                text_node_property=text_property,
                embedding_node_property=embedding_property
            ),
            # Try method 3: Using 'embed_model'
            lambda: Neo4jVector(
                embed_model=embeddings,
                url="bolt://localhost:7687",
                username=os.getenv("NEO4J_USERNAME"),
                password=os.getenv("NEO4J_PASSWORD"),
                index_name=index_name,
                node_label=node_label,
                text_node_property=text_property,
                embedding_node_property=embedding_property
            ),
            # Try method 4: Direct initialization without specifying embeddings
            lambda: Neo4jVector(
                url="bolt://localhost:7687",
                username=os.getenv("NEO4J_USERNAME"),
                password=os.getenv("NEO4J_PASSWORD"),
                index_name=index_name,
                node_label=node_label,
                text_node_property=text_property,
                embedding_node_property=embedding_property
            )
        ]
                                   
        # Try each method
        for i, method in enumerate(try_methods):
            try:
                print(f"  Trying initialization method {i+1}...")
                vector_store = method()
                print(f"  ✓ Method {i+1} succeeded!")
                return vector_store
            except Exception as e_method:
                print(f"  ❌ Method {i+1} failed: {e_method}")
        
        # If all methods fail, return None
        print("  ❌ All initialization methods failed.")
        return None
                


def vector_search(vector_store, query, k=3):
    """Perform vector search and return results."""
    try:
        docs = vector_store.similarity_search(query, k=k)
        return docs
    except Exception as e:
        print(f"❌ Error during vector search: {e}")
        return []


def generate_cypher_query(query, llm, graph):
    """Generate a Cypher query from a natural language query using LLM."""
    # Get information about the graph
    try:
        # Get all labels
        label_result = graph.query("CALL db.labels() YIELD label RETURN label")
        labels = [record["label"] for record in label_result]
        
        # Get all relationship types
        rel_result = graph.query("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType")
        rel_types = [record["relationshipType"] for record in rel_result]
        
        # Get node and relationship counts
        node_count = graph.query("MATCH (n) RETURN count(n) AS count")[0]["count"]
        rel_count = graph.query("MATCH ()-[r]->() RETURN count(r) AS count")[0]["count"]
    except Exception as e:
        print(f"Warning: Could not get complete graph information: {e}")
        # Fallback to empty values
        labels = []
        rel_types = []
        node_count = 0
        rel_count = 0
    
    # Create prompt template
    prompt_template = """
    You are an expert Neo4j Cypher query generator. Your task is to convert a natural language query into an appropriate Cypher query.

    GRAPH INFORMATION:
    - Labels: {labels}
    - Relationship types: {relationship_types}
    - Total nodes: {total_nodes}
    - Total relationships: {total_relationships}

    USER QUERY:
    {query}

    When generating the Cypher query, consider:
    1. Use appropriate labels and relationship types from the provided graph information
    2. Limit results to a reasonable number (usually 20-30 nodes at most)
    3. Include useful node properties in the RETURN statement
    4. Use pattern matching to find relevant connections between entities
    5. For property searches, use case-insensitive matching when appropriate (toLower, CONTAINS, etc.)
    6. Return results in a meaningful order

    Return only the Cypher query without any explanations or comments. 
    """
    
    prompt = PromptTemplate.from_template(prompt_template)
    
    # Create chain
    chain = (
        prompt
        | llm
        | StrOutputParser()
    )
    
    # Generate and clean the query
    generated_query = chain.invoke({
        "labels": labels,
        "relationship_types": rel_types,
        "total_nodes": node_count,
        "total_relationships": rel_count,
        "query": query
    }).strip()
    
    # Clean up the query by removing markdown code formatting if present
    if generated_query.startswith("```") and generated_query.endswith("```"):
        # Remove the first line containing ```cypher or ```
        lines = generated_query.split("\n")
        # Remove first and last lines (the ``` markers)
        generated_query = "\n".join(lines[1:-1])
    
    return generated_query


def llm_graph_search(graph, query, llm, k=5):
    """
    Perform a graph-based search using LLM-generated Cypher queries.
    This is more sophisticated than simple keyword matching.
    """
    print(f"Generating Cypher query for: '{query}'")
    
    try:
        # Generate Cypher query using LLM
        cypher_query = generate_cypher_query(query, llm, graph)
        print(f"Generated Cypher query: {cypher_query}")
        
        # Execute the query
        result = graph.query(cypher_query)
        print(f"Found {len(result)} results via LLM-powered graph search")
        
        # Convert results to documents
        docs = []
        for item in result:
            # Process each key in the result
            for key, value in item.items():
                # Skip paths and complex objects
                if key.lower() == "path" or not isinstance(value, dict):
                    continue
                
                # This is likely a node
                node = value
                
                # Determine text content from various properties
                if "text" in node and node["text"]:
                    content = node["text"]
                elif "description" in node and node["description"]:
                    content = node["description"]
                elif "content" in node and node["content"]:
                    content = node["content"]
                elif "name" in node and node["name"]:
                    # For nodes with just a name, try to enrich with type info
                    if "labels" in item:
                        node_type = item["labels"][0] if item["labels"] else "Entity"
                        content = f"{node_type}: {node['name']}"
                    else:
                        content = f"Entity: {node['name']}"
                else:
                    # Try to construct content from available properties
                    content_parts = []
                    for prop_key, prop_value in node.items():
                        if isinstance(prop_value, str) and len(prop_value) > 5:
                            content_parts.append(f"{prop_key}: {prop_value}")
                    
                    content = "\n".join(content_parts) if content_parts else str(node)
                
                # Prepare metadata (all node properties except content)
                metadata = {k: v for k, v in node.items() if k != "text" and k != "content" and k != "description"}
                if "labels" in item:
                    metadata["node_labels"] = item["labels"]
                
                # Create document
                doc = Document(
                    page_content=content,
                    metadata=metadata
                )
                docs.append(doc)
        
        # If we have too many results, limit to k
        if len(docs) > k:
            docs = docs[:k]
            
        return docs
        
    except Exception as e:
        print(f"❌ Error in LLM graph search: {e}")
        # Fall back to keyword-based search
        print("Falling back to keyword-based search...")
        return fallback_graph_search(graph, query, k)


def fallback_graph_search(graph, query, k=5):
    """
    Perform a simple keyword-based graph search as a fallback.
    """
    # Extract potential keywords from the query
    stop_words = {"what", "is", "are", "the", "to", "from", "in", "on", "of", "for", "a", "an", "and", "or", "but", "not"}
    keywords = [word.lower() for word in query.split() if word.lower() not in stop_words]
    
    # Prepare the Cypher query
    cypher_query = """
    MATCH (n)
    WHERE any(keyword IN $keywords WHERE toLower(n.name) CONTAINS keyword)
       OR any(keyword IN $keywords WHERE n.text IS NOT NULL AND toLower(n.text) CONTAINS keyword)
       OR any(keyword IN $keywords WHERE n.description IS NOT NULL AND toLower(n.description) CONTAINS keyword)
    RETURN n, labels(n) AS labels
    LIMIT $limit
    """
    
    # Execute the query
    try:
        result = graph.query(cypher_query, params={"keywords": keywords, "limit": k})
        
        # Convert results to documents
        docs = []
        for item in result:
            node = item["n"]
            node_labels = item["labels"]
            
            # Determine text content - prefer n.text but fallback to other properties
            if "text" in node and node["text"]:
                content = node["text"]
            elif "content" in node and node["content"]:
                content = node["content"]
            elif "description" in node and node["description"]:
                content = node["description"]
            else:
                # Try to construct content from available properties
                content_parts = []
                for key, value in node.items():
                    if isinstance(value, str) and len(value) > 20:  # Likely a text field
                        content_parts.append(f"{key}: {value}")
                content = "\n".join(content_parts) if content_parts else str(node)
            
            # Prepare metadata
            metadata = {k: v for k, v in node.items() if k != "text"}
            metadata["node_labels"] = node_labels
            
            # Create document
            doc = Document(
                page_content=content,
                metadata=metadata
            )
            docs.append(doc)
        
        return docs
    except Exception as e:
        print(f"❌ Error during fallback graph search: {e}")
        return []


def relationship_context(graph, docs, k=3):
    """
    Find relationships related to the nodes in the documents.
    This adds context about how entities are connected.
    """
    related_info = []
    
    for doc in docs:
        # Extract identifiers from metadata
        node_id = doc.metadata.get("id")
        if not node_id:
            # Try other potential identifier properties
            node_internal_id = doc.metadata.get("internal_id")
            node_name = doc.metadata.get("name")
            
            if not (node_internal_id or node_name):
                continue
            
            # Build query based on available identifiers
            where_clause = ""
            params = {"limit": k}
            
            if node_internal_id:
                where_clause = "elementId(n) = $internal_id"
                params["internal_id"] = node_internal_id
            elif node_name:
                where_clause = "n.name = $name"
                params["name"] = node_name
            
            # Skip if we couldn't build a query
            if not where_clause:
                continue
                
            # Query for relationships
            cypher_query = f"""
            MATCH (n)-[r]-(m)
            WHERE {where_clause}
            RETURN type(r) AS relationship, 
                n.name AS source_name,
                m.name AS target_name,
                labels(n) AS source_labels,
                labels(m) AS target_labels
            LIMIT $limit
            """
        else:
            # We have an id, use it
            cypher_query = """
            MATCH (n)-[r]-(m)
            WHERE n.id = $node_id
            RETURN type(r) AS relationship, 
                n.name AS source_name,
                m.name AS target_name,
                labels(n) AS source_labels,
                labels(m) AS target_labels
            LIMIT $limit
            """
            params = {"node_id": node_id, "limit": k}
        
        try:
            result = graph.query(cypher_query, params=params)
            
            for item in result:
                # Skip if we're missing essential data
                if not (item.get('source_name') and item.get('target_name') and item.get('relationship')):
                    continue
                    
                relation_info = f"{item['source_name']} [{item['relationship']}] {item['target_name']}"
                related_info.append(relation_info)
        except Exception as e:
            print(f"❌ Error querying relationships: {e}")
    
    # Return unique relationships
    return list(set(related_info))


def enhanced_relationship_search(graph, docs, query, llm, k=5):
    """
    Use LLM to generate relationship search queries based on the user's question.
    This provides deeper graph traversal than simple relationship retrieval.
    """
    if not docs:
        return []
    
    # Extract entity names from documents to search for relationships
    entity_names = []
    for doc in docs:
        if "name" in doc.metadata and doc.metadata["name"]:
            entity_names.append(doc.metadata["name"])
        elif "id" in doc.metadata and doc.metadata["id"]:
            entity_names.append(doc.metadata["id"])
    
    # If we don't have enough entities, return empty list
    if len(entity_names) == 0:
        return []
    
    # Limit to top 5 entities to avoid complex queries
    entity_names = entity_names[:5]
    
    # Create a prompt to generate a relationship query
    relationship_prompt = f"""
    Given the user's question: "{query}"
    
    And these entities found in our knowledge graph: {', '.join(entity_names)}
    
    Generate a Cypher query to find relationships between these entities or other related entities 
    that would help answer the user's question. 
    
    Focus on finding paths that connect these entities or show how they relate to other important entities.
    Limit results to {k} relationships.
    
    Return ONLY the Cypher query without any explanation.
    """
    
    try:
        # Generate the Cypher query
        cypher_query = llm.invoke(relationship_prompt).strip()
        
        # Clean up the query by removing markdown code formatting if present
        if cypher_query.startswith("```") and cypher_query.endswith("```"):
            lines = cypher_query.split("\n")
            cypher_query = "\n".join(lines[1:-1])
        
        print(f"Generated relationship query: {cypher_query}")
        
        # Execute the query
        result = graph.query(cypher_query)
        
        # Format relationship information
        relationship_info = []
        
        for item in result:
            # Try different formats depending on what was returned
            if "path" in item:
                # Path was returned - format it as a series of relationships
                # (This is a complex case, simplified here)
                path_info = f"Path found connecting entities (length: {len(item['path'])})"
                relationship_info.append(path_info)
            elif all(k in item for k in ["source", "relationship", "target"]):
                # Direct relationship format
                source = item.get("source", {}).get("name", "Unknown")
                target = item.get("target", {}).get("name", "Unknown")
                rel_type = item.get("relationship", "connected to")
                
                relationship_info.append(f"{source} [{rel_type}] {target}")
            elif "r" in item and isinstance(item["r"], dict):
                # Relationship object returned
                rel_info = f"Relationship: {item['r'].get('type', 'connects')} with properties: {item['r']}"
                relationship_info.append(rel_info)
            else:
                # Try to extract relationship information from any format
                rel_str = str(item)
                if len(rel_str) < 200:  # Only add if it's reasonably short
                    relationship_info.append(rel_str)
        
        return relationship_info
        
    except Exception as e:
        print(f"❌ Error in enhanced relationship search: {e}")
        # Fall back to basic relationship context
        return []


def combine_search_results(vector_results, graph_results, llm_graph_results, relationship_info):
    """Combine results from vector and graph searches, removing duplicates."""
    # Track seen content to avoid duplicates
    seen_content = set()
    combined_docs = []
    
    # Create scores to track search method priorities (for ranking)
    scores = {}
    
    # Process vector results first with highest priority
    for i, doc in enumerate(vector_results):
        # Create a fingerprint of the content to detect duplicates
        content_fingerprint = doc.page_content[:100]  # Use the first 100 chars as fingerprint
        if content_fingerprint not in seen_content:
            seen_content.add(content_fingerprint)
            combined_docs.append(doc)
            # Add a score based on position (higher for earlier results)
            scores[content_fingerprint] = 100 - i  # Vector results get highest scores
    
    # Then add LLM-powered graph results with medium priority
    for i, doc in enumerate(llm_graph_results):
        content_fingerprint = doc.page_content[:100]
        if content_fingerprint not in seen_content:
            seen_content.add(content_fingerprint)
            combined_docs.append(doc)
            # Add a score based on position
            scores[content_fingerprint] = 70 - i  # LLM graph results get medium scores
    
    # Then add keyword-based graph results with lowest priority
    for i, doc in enumerate(graph_results):
        content_fingerprint = doc.page_content[:100]
        if content_fingerprint not in seen_content:
            seen_content.add(content_fingerprint)
            combined_docs.append(doc)
            # Add a score based on position
            scores[content_fingerprint] = 40 - i  # Basic graph results get lowest scores
    
    # Sort combined docs based on scores
    sorted_docs = sorted(
        combined_docs,
        key=lambda doc: scores.get(doc.page_content[:100], 0),
        reverse=True
    )
    
    return sorted_docs, relationship_info


def format_context(docs, relationship_info):
    """Format the context from documents and relationships for the prompt."""
    context_parts = []
    
    # Add document content
    for i, doc in enumerate(docs):
        # Extract label and name for a nice header
        label = "Unknown"
        if "node_labels" in doc.metadata:
            if isinstance(doc.metadata["node_labels"], list) and doc.metadata["node_labels"]:
                label = doc.metadata["node_labels"][0]
            elif isinstance(doc.metadata["node_labels"], str):
                label = doc.metadata["node_labels"]
        
        name = doc.metadata.get("name", f"Item {i+1}")
        
        # Add a header with label and name
        context_parts.append(f"--- {label}: {name} ---")
        
        # Add key metadata that might be important
        important_metadata = ["id", "type", "category", "created", "source"]
        metadata_parts = []
        for key in important_metadata:
            if key in doc.metadata and doc.metadata[key]:
                metadata_parts.append(f"{key}: {doc.metadata[key]}")
        
        if metadata_parts:
            context_parts.append("Metadata: " + ", ".join(metadata_parts))
        
        # Add the actual content
        context_parts.append(doc.page_content)
        context_parts.append("")  # Empty line for separation
    
    # Add relationship information if available
    if relationship_info and len(relationship_info) > 0:
        context_parts.append("--- Entity Relationships ---")
        for rel in relationship_info:
            context_parts.append(f"- {rel}")
    
    return "\n".join(context_parts)


def create_enhanced_rag_chain(llm, vector_store, graph):
    """Create an enhanced hybrid RAG chain with LLM-powered graph search."""
    
    # Define the hybrid retrieval function
    def enhanced_hybrid_retrieval(query_dict):
        # Extract the query string
        if isinstance(query_dict, dict) and "query" in query_dict:
            query = query_dict["query"]
        elif isinstance(query_dict, str):
            query = query_dict
        else:
            raise ValueError(f"Expected str or dict with 'query' key, got {type(query_dict)}: {query_dict}")
            
        # Step 1: Vector search
        print(f"Performing vector search for: '{query}'")
        vector_results = vector_search(vector_store, query, k=3)
        print(f"  Found {len(vector_results)} results via vector search")
        
        # Step 2: LLM-powered graph search
        print(f"Performing LLM-powered graph search for: '{query}'")
        llm_graph_results = llm_graph_search(graph, query, llm, k=3)
        print(f"  Found {len(llm_graph_results)} results via LLM-powered graph search")
        
        # Step 3: Basic fallback graph search (as a last resort)
        print(f"Performing fallback graph search for: '{query}'")
        graph_results = fallback_graph_search(graph, query, k=3)
        print(f"  Found {len(graph_results)} results via basic graph search")
        
        # Step 4: Get basic relationship context
        print("Retrieving relationship context...")
        rel_info = relationship_context(graph, vector_results + llm_graph_results, k=5)
        print(f"  Found {len(rel_info)} basic relationships")
        
        # Step 5: Get enhanced relationship information using LLM
        print("Retrieving enhanced relationship information...")
        enhanced_rel_info = enhanced_relationship_search(
            graph,
            vector_results + llm_graph_results,
            query,
            llm,
            k=3
        )
        print(f"  Found {len(enhanced_rel_info)} enhanced relationships")
        
        # Combine all relationship information
        all_rel_info = rel_info + enhanced_rel_info
        
        # Step 6: Combine results
        combined_docs, relationships = combine_search_results(
            vector_results, graph_results, llm_graph_results, all_rel_info
        )
        
        # Step 7: Format context
        context = format_context(combined_docs, relationships)
        
        return {"context": context, "question": query}
    
    # Create prompt template with additional guidance
    prompt = ChatPromptTemplate.from_template("""
    You are an intelligent and knowledgeable assistant with access to information from a knowledge graph.
    Use the following context to answer the question. The context contains information about
    entities from a graph database and how they are related to each other.
    
    When answering:
    - Focus on relationships between entities when they're relevant to the question
    - Consider how different entities are connected in the graph
    - If multiple entities are mentioned, explain how they relate to each other
    - If you don't know the answer based on the provided context, say so clearly
    
    Context:
    {context}
    
    Question: {question}
    
    Answer:
    """)
    
    # Create chain - fix the input for RunnablePassthrough
    chain = (
        {"query": RunnablePassthrough()} 
        | RunnablePassthrough.assign(retriever_output=enhanced_hybrid_retrieval)
        | RunnablePassthrough.assign(
            context=lambda x: x["retriever_output"]["context"],
            question=lambda x: x["retriever_output"]["question"],
        )
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain


def main():
    parser = argparse.ArgumentParser(description="Enhanced Neo4j Hybrid RAG for Question Answering")
    parser.add_argument("--index", help="Vector index name to use")
    parser.add_argument("--model", default="nomic-embed-text:latest", help="Ollama model to use for embeddings")
    parser.add_argument("--llm", default="llama3-chatqa:8b", help="Ollama model to use for text generation")
    parser.add_argument("--list-indices", action="store_true", help="List all available vector indices")
    parser.add_argument("--temperature", type=float, default=0.1, help="LLM temperature")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("question", nargs="?", help="Question to answer (not needed in interactive mode)")
    
    args = parser.parse_args()
    
    # Set up global verbosity
    global VERBOSE
    VERBOSE = args.verbose
    
    # Initialize Neo4j connection
    graph = initialize_neo4j_connection()
    
    # List all available indices if requested
    if args.list_indices:
        indices = get_available_vector_indices(graph)
        print("\nAvailable vector indices in Neo4j:")
        for idx in indices:
            print(f"  - {idx}")
        return
    
    # We need an index name
    if not args.index:
        indices = get_available_vector_indices(graph)
        if not indices:
            print("❌ No vector indices found in the database. Please create vectors first.")
            return
        
        print("\nAvailable vector indices in Neo4j:")
        for i, idx in enumerate(indices):
            print(f"  {i+1}. {idx}")
        
        selection = input("\nSelect an index by number (or press Enter to use the first one): ")
        if selection.strip() and selection.isdigit() and 1 <= int(selection) <= len(indices):
            index_name = indices[int(selection) - 1]
        else:
            index_name = indices[0]
        
        print(f"Using index: {index_name}")
    else:
        index_name = args.index
    
    # Initialize components
    try:
        embeddings = initialize_embeddings(model_name=args.model)
        llm = initialize_llm(model_name=args.llm, temperature=args.temperature)
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        print("\nHint: Make sure Ollama is running and has the required models.")
        print("You can install models with: ollama pull <model-name>")
        print("Example: ollama pull nomic-embed-text:latest")
        print("Example: ollama pull llama3-chatqa:8b")
        return
    
    # Load vector store
    vector_store = load_vector_store(graph, embeddings, index_name)
    if not vector_store:
        print("❌ Failed to create vector store. Please check your Neo4j configuration.")
        return
    
    # Create enhanced RAG chain
    rag_chain = create_enhanced_rag_chain(llm, vector_store, graph)
    
    # Interactive mode or single question
    if args.interactive:
        print("\n" + "="*50)
        print("INTERACTIVE QUESTION ANSWERING")
        print("Type 'exit' or 'quit' to end the session")
        print("="*50 + "\n")
        
        while True:
            question = input("\nEnter your question: ")
            if question.lower() in ("exit", "quit"):
                break
            
            if not question.strip():
                continue
            
            print("\nProcessing...")
            try:
                answer = rag_chain.invoke(question)
                print("\n" + "-"*50)
                print("ANSWER:")
                print("-"*50)
                print(answer)
            except Exception as e:
                print(f"❌ Error: {e}")
                if args.verbose:
                    import traceback
                    traceback.print_exc()
                print("\nTry asking a different question or using different models.")
    
    elif args.question:
        try:
            answer = rag_chain.invoke(args.question)
            print("\n" + "-"*50)
            print("ANSWER:")
            print("-"*50)
            print(answer)
        except Exception as e:
            print(f"❌ Error: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
    
    else:
        print("❌ No question provided. Use --interactive or provide a question.")
        print("You can also use --help to see all available options.")


if __name__ == "__main__":
    main()