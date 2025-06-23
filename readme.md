# Getting started

1. Setup virtual environment
mkdir X
cd X
python3 -m venv .

2. Activate virtual enviroment
source ./bin/activate

3. Install langchain
https://python.langchain.com/v0.1/docs/get_started/installation/

pip install langchain


# Neo4j Knowledge Graph and RAG System

This project provides scripts to create a knowledge graph from documents, convert the graph data into vector embeddings, and implement a hybrid retrieval-augmented generation (RAG) system for question answering.

## Overview

The workflow consists of three main components:

1. **Document to Graph** - Extracts entities and relationships from documents and stores them in Neo4j
2. **Graph to Vector Store** - Creates embeddings from graph nodes and stores them in Neo4j
3. **Hybrid RAG** - Combines vector search and graph traversal for better question answering

## Prerequisites

- Docker (for running Neo4j container)
- Python 3.8+
- Ollama running locally (for embeddings and LLM)
- Required Python packages:
  - langchain
  - langchain-community
  - neo4j
  - python-dotenv
  - tqdm

## Setup

1. Create a `.env` file with your Neo4j credentials:

```
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
```

2. Start a Neo4j Docker container:

```bash
docker run -d \
  --name neo4j-graph \
  -p 7474:7474 -p 7687:7687 \
  -v $PWD/neo4j/data:/data \
  -v $PWD/neo4j/logs:/logs \
  -v $PWD/neo4j/import:/import \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.9
```

3. Start Ollama and make sure you have the required models:

```bash
# Install Ollama if needed
# Start Ollama service
ollama pull llama3  # Pull the model you want to use
```

## Usage

### 1. Process Documents into Graph

The document processor extracts entities and relationships from documents and stores them in Neo4j:

```bash
python neo4j_2c-langchain-document-to-graph-adaptive.py path/to/document.pdf --adaptive --save
```

Options:
- `--adaptive`: Automatically adjust chunk size based on document length
- `--save`: Save extracted data for later use
- `--parallel`: Process chunks in parallel
- `--workers N`: Number of worker threads for parallel processing

### 2. Create Vector Store from Graph

Convert graph nodes into vector embeddings for semantic search:

```bash
# List available node types
python neo4j_3-langchain-graph-to-vector-store.py --list-labels

# Process specific node type
python neo4j_3-langchain-graph-to-vector-store.py --label Person --text-property text

# Process all node types
python neo4j_3-langchain-graph-to-vector-store.py --all

# Test with a query
python neo4j_3-langchain-graph-to-vector-store.py --label Person --test-query "Who is the CEO?"
```

Options:
- `--list-labels`: Show all available node labels in the graph
- `--label`: Specify which node type to process
- `--text-property`: Property containing text content (auto-detected if not specified)
- `--filter`: Additional Cypher filter condition
- `--all`: Process all node types
- `--model`: Ollama embedding model to use (default: llama3)
- `--test-query`: Test query for the created vector store

### 3. Hybrid RAG for Question Answering

Use both vector search and graph relationships for better question answering:

```bash
# List available vector indices
python neo4j_hybrid_rag.py --list-indices

# Interactive Q&A session
python neo4j_hybrid_rag.py --interactive

# Answer a specific question
python neo4j_hybrid_rag.py --index person_text "Who founded the company?"
```

Options:
- `--list-indices`: Show all available vector indices
- `--index`: Specify which vector index to use
- `--model`: Ollama model to use (default: llama3)
- `--temperature`: LLM temperature (default: 0.1)
- `--interactive`: Run in interactive mode

### Complete Workflow

You can run the entire workflow using the provided shell script:

```bash
chmod +x neo4j_workflow.sh
./neo4j_workflow.sh
```

## How It Works

### Document to Graph

1. Document is loaded and split into chunks
2. LLM extracts entities and relationships from each chunk
3. Extracted data is merged and stored in Neo4j
4. Entities become nodes, relationships become edges

### Graph to Vector Store

1. Node text content is extracted from the graph
2. Text is converted to embeddings using Ollama
3. Embeddings are stored in Neo4j as vector indices
4. Each node type gets its own vector index

### Hybrid RAG

1. Query is processed through both vector search and keyword search
2. Vector search finds semantically similar content
3. Graph search finds relevant nodes based on keywords
4. Relationship context adds graph structure information
5. Combined context is sent to LLM for answering

## Benefits of Hybrid RAG

- **Better context retrieval**: Combines semantic similarity with structural relationships
- **Entity awareness**: Understands the connections between entities
- **More accurate answers**: Provides contextually relevant information

## Advanced Usage

### Custom Filtering

You can filter which nodes get vectorized:

```bash
# Only vectorize Person nodes with a 'role' property
python neo4j_3-langchain-graph-to-vector-store.py --label Person --filter "n.role IS NOT NULL"
```

### Different Embedding Models

Change the embedding model:

```bash
# Use a different Ollama model
python neo4j_3-langchain-graph-to-vector-store.py --label Document --model gemma3:2b
```

### Adjusting RAG Parameters

Fine-tune the RAG system:

```bash
# Use a different LLM with higher temperature
python neo4j_hybrid_rag.py --model gemma3:12b --temperature 0.7
```

## Troubleshooting

- **Neo4j connection issues**: Check that the Neo4j container is running and credentials are correct
- **Empty vector store**: Ensure nodes have text content in the specified property
- **Ollama errors**: Make sure Ollama is running and the requested model is available
- **Memory issues**: For large documents, try processing in smaller chunks using `--start-chunk` and `--end-chunk`

## Advanced Graph Queries

You can directly query the Neo4j graph using the browser interface at http://localhost:7474.

Example Cypher queries:

```cypher
// Find all entity types
MATCH (n)
RETURN DISTINCT labels(n) AS EntityType, count(*) AS Count
ORDER BY Count DESC;

// Find connections between entities
MATCH (a)-[r]->(b)
RETURN DISTINCT type(r) AS RelationType, count(*) AS Count
ORDER BY Count DESC;

// Find paths between specific entities
MATCH path = shortestPath((a:Person {name: "John"})-[*]-(b:Organization {name: "Acme Inc"}))
RETURN path;
```