# neo4j_hybrid_rag.py
import os
import argparse
from dotenv import load_dotenv
import warnings

# LangChain imports
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain.schema import Document
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

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


def initialize_llm(model_name="llama3-chatqa:8b", temperature=0.1):
    """Initialize and return the LLM."""
    # List of models to try in order of preference
    models_to_try = [
        model_name,        # Try the specified model first
        "llama3-chatqa:8b",      # Good QA model
        "llama3:8b",       # Alternative
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


def graph_search(graph, query, k=3):
    """
    Perform a graph-based search to find relevant nodes.
    This will use a keyword-based approach to find relevant nodes.
    """
    # Extract potential keywords from the query
    # This is a simple approach - in production, you might use NLP for better extraction
    stop_words = {"what", "is", "are", "the", "to", "from", "in", "on", "of", "for", "a", "an", "and", "or", "but", "not"}
    keywords = [word.lower() for word in query.split() if word.lower() not in stop_words]
    
    # Prepare the Cypher query
    cypher_query = """
    MATCH (n)
    WHERE any(keyword IN $keywords WHERE toLower(n.name) CONTAINS keyword)
       OR any(keyword IN $keywords WHERE n.text IS NOT NULL AND toLower(n.text) CONTAINS keyword)
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
            if "text" in node:
                content = node["text"]
            elif "content" in node:
                content = node["content"]
            elif "description" in node:
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
        print(f"❌ Error during graph search: {e}")
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
            continue
        
        # Query for relationships
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
        
        try:
            result = graph.query(cypher_query, params={"node_id": node_id, "limit": k})
            
            for item in result:
                relation_info = f"{item['source_name']} [{item['relationship']}] {item['target_name']}"
                related_info.append(relation_info)
        except Exception as e:
            print(f"❌ Error querying relationships: {e}")
    
    # Return unique relationships
    return list(set(related_info))


def combine_search_results(vector_results, graph_results, relationship_info):
    """Combine results from vector and graph searches, removing duplicates."""
    # Track seen content to avoid duplicates
    seen_content = set()
    combined_docs = []
    
    # Process vector results first (they're often more relevant)
    for doc in vector_results:
        # Create a fingerprint of the content to detect duplicates
        content_fingerprint = doc.page_content[:100]  # Use the first 100 chars as fingerprint
        if content_fingerprint not in seen_content:
            seen_content.add(content_fingerprint)
            combined_docs.append(doc)
    
    # Then add graph results if they're not duplicates
    for doc in graph_results:
        content_fingerprint = doc.page_content[:100]
        if content_fingerprint not in seen_content:
            seen_content.add(content_fingerprint)
            combined_docs.append(doc)
    
    return combined_docs, relationship_info


def format_context(docs, relationship_info):
    """Format the context from documents and relationships for the prompt."""
    context_parts = []
    
    # Add document content
    for i, doc in enumerate(docs):
        # Extract label and name for a nice header
        label = doc.metadata.get("node_labels", ["Item"])[0] if isinstance(doc.metadata.get("node_labels"), list) else "Item"
        name = doc.metadata.get("name", f"Item {i+1}")
        
        context_parts.append(f"--- {label}: {name} ---")
        context_parts.append(doc.page_content)
        context_parts.append("")  # Empty line for separation
    
    # Add relationship information if available
    if relationship_info and len(relationship_info) > 0:
        context_parts.append("--- Entity Relationships ---")
        for rel in relationship_info:
            context_parts.append(f"- {rel}")
    
    return "\n".join(context_parts)


def create_rag_chain(llm, vector_store, graph):
    """Create a hybrid RAG chain combining vector search and graph context."""
    
    # Define the hybrid retrieval function
    def hybrid_retrieval(query_dict):
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
        
        # Step 2: Graph search
        print(f"Performing graph search for: '{query}'")
        graph_results = graph_search(graph, query, k=3)
        print(f"  Found {len(graph_results)} results via graph search")
        
        # Step 3: Get relationship context
        print("Retrieving relationship context...")
        rel_info = relationship_context(graph, vector_results + graph_results, k=5)
        print(f"  Found {len(rel_info)} relationships")
        
        # Step 4: Combine results
        combined_docs, relationships = combine_search_results(
            vector_results, graph_results, rel_info
        )
        
        # Step 5: Format context
        context = format_context(combined_docs, relationships)
        
        return {"context": context, "question": query}
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_template("""
    You are a knowledgeable assistant with access to information from a knowledge graph.
    Use the following context to answer the question. If you don't know the answer 
    based on the provided context, say so clearly rather than making up information.

    Context:
    {context}
    
    Question: {question}
    
    Answer:
    """)
    
    # Create chain - fix the input for RunnablePassthrough
    chain = (
        {"query": RunnablePassthrough()} 
        | RunnablePassthrough.assign(retriever_output=hybrid_retrieval)
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
    parser = argparse.ArgumentParser(description="Neo4j Hybrid RAG for Question Answering")
    parser.add_argument("--index", help="Vector index name to use")
    parser.add_argument("--model", default="nomic-embed-text:latest", help="Ollama model to use for embeddings")
    parser.add_argument("--llm", default="sciphi/triplex", help="Ollama model to use for text generation")
    parser.add_argument("--list-indices", action="store_true", help="List all available vector indices")
    parser.add_argument("--temperature", type=float, default=0.1, help="LLM temperature")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--list-models", action="store_true", help="List available Ollama models")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("question", nargs="?", help="Question to answer (not needed in interactive mode)")
    
    args = parser.parse_args()
    
    # Set up global verbosity
    global VERBOSE
    VERBOSE = args.verbose
    
    # Check for available Ollama models if requested
    if args.list_models:
        try:
            import requests
            print("\nChecking for available Ollama models...")
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                print("\nAvailable Ollama models:")
                for model in models:
                    print(f"  - {model.get('name')}")
            else:
                print(f"❌ Failed to get Ollama models: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Error checking Ollama models: {e}")
        return
    
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
        print("Example: ollama pull sciphi/triplex")
        return
    
    # Load vector store
    vector_store = load_vector_store(graph, embeddings, index_name)
    if not vector_store:
        print("❌ Failed to create vector store. Please check your Neo4j configuration.")
        return
    
    # Create RAG chain
    rag_chain = create_rag_chain(llm, vector_store, graph)
    
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