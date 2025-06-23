# neo4j_5-llm-graph-search.py
import os
import argparse
from dotenv import load_dotenv
import warnings
from typing import List, Dict, Any, Optional
import time

# LangChain imports
from langchain_community.graphs import Neo4jGraph
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnablePassthrough
from langchain.chains.llm import LLMChain

# Load environment variables from .env file
load_dotenv()
warnings.filterwarnings("ignore")

# Global verbose flag
VERBOSE = False

def initialize_neo4j_connection() -> Optional[Neo4jGraph]:
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
        return None

def initialize_llm(model_name: str = "llama3.1:latest", temperature: float = 0.1) -> Ollama:
    """Initialize and return the LLM."""
    # List of models to try in order of preference
    models_to_try = [
        model_name,        # Try the specified model first
        "gemma3:12b",       # Good general model
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

def get_node_labels(graph: Neo4jGraph) -> List[str]:
    """Get all node labels in the graph."""
    try:
        result = graph.query("CALL db.labels() YIELD label RETURN label")
        return [record["label"] for record in result]
    except Exception as e:
        print(f"❌ Error getting node labels: {e}")
        return []

def get_relationship_types(graph: Neo4jGraph) -> List[str]:
    """Get all relationship types in the graph."""
    try:
        result = graph.query("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType")
        return [record["relationshipType"] for record in result]
    except Exception as e:
        print(f"❌ Error getting relationship types: {e}")
        return []

def get_graph_stats(graph: Neo4jGraph) -> Dict[str, Any]:
    """Get statistics about the graph."""
    stats = {}
    
    # Get total node count
    try:
        result = graph.query("MATCH (n) RETURN count(n) AS node_count")
        stats["total_nodes"] = result[0]["node_count"]
    except Exception as e:
        print(f"❌ Error getting node count: {e}")
        stats["total_nodes"] = 0
    
    # Get total relationship count
    try:
        result = graph.query("MATCH ()-[r]->() RETURN count(r) AS rel_count")
        stats["total_relationships"] = result[0]["rel_count"]
    except Exception as e:
        print(f"❌ Error getting relationship count: {e}")
        stats["total_relationships"] = 0
    
    # Get count by label
    labels = get_node_labels(graph)
    stats["label_counts"] = {}
    
    for label in labels:
        try:
            result = graph.query(f"MATCH (n:{label}) RETURN count(n) AS count")
            stats["label_counts"][label] = result[0]["count"]
        except Exception as e:
            print(f"❌ Error getting count for label {label}: {e}")
            stats["label_counts"][label] = 0
    
    # Get count by relationship type
    rel_types = get_relationship_types(graph)
    stats["relationship_counts"] = {}
    
    for rel_type in rel_types:
        try:
            result = graph.query(f"MATCH ()-[r:{rel_type}]->() RETURN count(r) AS count")
            stats["relationship_counts"][rel_type] = result[0]["count"]
        except Exception as e:
            print(f"❌ Error getting count for relationship type {rel_type}: {e}")
            stats["relationship_counts"][rel_type] = 0
    
    return stats

# Define output schemas using Pydantic
class CypherQuery(BaseModel):
    """Schema for a generated Cypher query."""
    query: str = Field(description="The Cypher query to execute")
    explanation: str = Field(description="Explanation of what the query does")

class GraphSearchResult(BaseModel):
    """Schema for graph search results."""
    nodes: List[Dict[str, Any]] = Field(description="List of nodes found")
    relationships: List[Dict[str, Any]] = Field(description="List of relationships found")
    summary: str = Field(description="Summary of the search results")

def generate_cypher_query(query: str, llm: Ollama, graph_info: Dict[str, Any]) -> str:
    """Generate a Cypher query from a natural language query using LLM."""
    # Create a list of labels and relationship types
    labels = list(graph_info["label_counts"].keys())
    rel_types = list(graph_info["relationship_counts"].keys())
    
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
        "total_nodes": graph_info["total_nodes"],
        "total_relationships": graph_info["total_relationships"],
        "query": query
    }).strip()
    
    # Clean up the query by removing markdown code formatting if present
    if generated_query.startswith("```") and generated_query.endswith("```"):
        # Remove the first line containing ```cypher or ```
        lines = generated_query.split("\n")
        # Remove first and last lines (the ``` markers)
        generated_query = "\n".join(lines[1:-1])
    
    return generated_query

def execute_graph_search(query: str, graph: Neo4jGraph, llm: Ollama) -> Dict[str, Any]:
    """Execute a graph search based on natural language query."""
    # Get graph statistics
    graph_info = get_graph_stats(graph)
    
    print(f"\nGraph information:")
    print(f"- Total nodes: {graph_info['total_nodes']}")
    print(f"- Total relationships: {graph_info['total_relationships']}")
    print(f"- Labels: {', '.join(graph_info['label_counts'].keys())}")
    print(f"- Relationship types: {', '.join(graph_info['relationship_counts'].keys())}")
    
    # Generate Cypher query from natural language
    print(f"\nGenerating Cypher query for: '{query}'...")
    cypher_query = generate_cypher_query(query, llm, graph_info)
    
    print(f"\nGenerated Cypher query:")
    print(f"{cypher_query}")
    
    # Execute the query
    print(f"\nExecuting query...")
    try:
        start_time = time.time()
        result = graph.query(cypher_query)
        execution_time = time.time() - start_time
        
        print(f"✓ Query executed successfully in {execution_time:.2f} seconds")
        print(f"Found {len(result)} results")
        
        # Format results for display
        formatted_results = {
            "query": query,
            "cypher_query": cypher_query,
            "execution_time": execution_time,
            "result_count": len(result),
            "results": result
        }
        
        return formatted_results
    except Exception as e:
        print(f"❌ Error executing query: {e}")
        
        # Try to provide helpful feedback based on the error
        error_str = str(e)
        if "SyntaxError" in error_str:
            print(f"  This appears to be a syntax error in the generated Cypher query.")
            print(f"  Let's try to generate a simpler query...")
            
            # Generate a simpler fallback query
            fallback_query = f"""
            MATCH (n)
            WHERE toLower(n.name) CONTAINS toLower('{query}') 
               OR toLower(n.text) CONTAINS toLower('{query}')
            RETURN n LIMIT 10
            """
            
            try:
                print(f"\nExecuting fallback query:")
                print(fallback_query)
                
                start_time = time.time()
                result = graph.query(fallback_query)
                execution_time = time.time() - start_time
                
                print(f"✓ Fallback query executed successfully in {execution_time:.2f} seconds")
                print(f"Found {len(result)} results")
                
                # Format results for display
                formatted_results = {
                    "query": query,
                    "cypher_query": fallback_query,
                    "execution_time": execution_time,
                    "result_count": len(result),
                    "results": result,
                    "note": "Used fallback query due to error with LLM-generated query"
                }
                
                return formatted_results
            except Exception as e2:
                print(f"❌ Error executing fallback query: {e2}")
        
        return {
            "query": query,
            "cypher_query": cypher_query,
            "error": str(e),
            "result_count": 0,
            "results": []
        }

def format_search_results(results: Dict[str, Any], llm: Ollama) -> str:
    """Format search results in a human-readable way, with LLM summarization."""
    if results.get("error"):
        return f"Error: {results['error']}"
    
    if results.get("result_count", 0) == 0:
        return "No results found matching your query."
    
    # Format results as a string for display and LLM processing
    formatted_text = []
    formatted_text.append(f"Query: {results['query']}")
    formatted_text.append(f"Cypher: {results['cypher_query']}")
    formatted_text.append(f"Found {results['result_count']} results in {results['execution_time']:.2f} seconds")
    
    # Process each result
    for i, item in enumerate(results['results']):
        formatted_text.append(f"\nResult {i+1}:")
        
        # Process each key in the result
        for key, value in item.items():
            # Special handling for node objects
            if isinstance(value, dict) and key.lower() != "path":
                # This is likely a node
                formatted_text.append(f"  {key}:")
                for prop_key, prop_value in value.items():
                    if prop_value is not None:
                        formatted_text.append(f"    {prop_key}: {prop_value}")
            elif key.lower() != "path":  # Skip path objects as they're complex
                formatted_text.append(f"  {key}: {value}")
    
    # Generate a summary of the results using the LLM
    summary_prompt = f"""
    Summarize the following search results from a knowledge graph:
    
    {formatted_text}
    
    Provide a concise summary (2-3 sentences) that captures the key entities and relationships found.
    """
    
    try:
        summary = llm.invoke(summary_prompt)
        formatted_text.append(f"\nSummary: {summary}")
    except Exception as e:
        print(f"Warning: Could not generate summary: {e}")
    
    return "\n".join(formatted_text)

def interactive_graph_search(graph: Neo4jGraph, llm: Ollama):
    """Run an interactive graph search session."""
    print("\n" + "="*60)
    print("INTERACTIVE GRAPH SEARCH")
    print("Type 'exit' or 'quit' to end the session")
    print("="*60 + "\n")
    
    while True:
        query = input("\nEnter your search query: ")
        if query.lower() in ("exit", "quit"):
            break
        
        if not query.strip():
            continue
        
        print("\nSearching...")
        try:
            results = execute_graph_search(query, graph, llm)
            
            formatted_results = format_search_results(results, llm)
            
            print("\n" + "-"*60)
            print("SEARCH RESULTS:")
            print("-"*60)
            print(formatted_results)
        except Exception as e:
            print(f"❌ Error during search: {e}")
            if VERBOSE:
                import traceback
                traceback.print_exc()
            print("\nTry a different query or check your graph connection.")

def main():
    parser = argparse.ArgumentParser(description="LLM-powered Neo4j Graph Search")
    parser.add_argument("--model", default="llama3.1:latest", help="Ollama model to use for text generation")
    parser.add_argument("--temperature", type=float, default=0.1, help="LLM temperature")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("query", nargs="?", help="Search query (not needed in interactive mode)")
    
    args = parser.parse_args()
    
    # Set up global verbosity
    global VERBOSE
    VERBOSE = args.verbose
    
    # Initialize Neo4j connection
    graph = initialize_neo4j_connection()
    if not graph:
        return
    
    # Initialize LLM
    try:
        llm = initialize_llm(model_name=args.model, temperature=args.temperature)
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        print("\nHint: Make sure Ollama is running and has the required models.")
        print("You can install models with: ollama pull <model-name>")
        print("Example: ollama pull llama3.1:latest")
        return
    
    # Interactive mode or single query
    if args.interactive:
        interactive_graph_search(graph, llm)
    elif args.query:
        try:
            results = execute_graph_search(args.query, graph, llm)
            formatted_results = format_search_results(results, llm)
            
            print("\n" + "-"*60)
            print("SEARCH RESULTS:")
            print("-"*60)
            print(formatted_results)
        except Exception as e:
            print(f"❌ Error: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
    else:
        print("❌ No query provided. Use --interactive or provide a query.")
        print("You can also use --help to see all available options.")

if __name__ == "__main__":
    main()