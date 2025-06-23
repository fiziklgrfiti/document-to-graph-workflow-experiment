#!/bin/bash
# neo4j_workflow.sh - Full workflow for Neo4j knowledge graph creation and querying

# Setup colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if command succeeded
check_error() {
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERROR: $1${NC}"
        echo -e "${YELLOW}Workflow interrupted. Please fix the error and try again.${NC}"
        exit 1
    fi
}

# Display header
echo -e "\n${GREEN}=== NEO4J KNOWLEDGE GRAPH WORKFLOW ===${NC}\n"

# Step 1: Check if Neo4j is running and start if needed
echo -e "${YELLOW}Step 1: Checking Neo4j status...${NC}"
image_name="langchain-examples-neo4j"

# Check if a container with the langchain-examples-neo4j image is running
if [ "$(docker ps -q -f ancestor=$image_name)" ]; then
    echo -e "${GREEN}✓ A Neo4j container with image $image_name is already running.${NC}"
else
    # If not running, check if we need to start our docker-compose setup
    echo "No Neo4j container found running with image $image_name. Starting docker-compose..."
    docker compose up -d
    check_error "Failed to start Docker container. Is Docker running?"

    echo "Waiting for Neo4j to start up (this may take a minute)..."
    # Give Neo4j more time to start
    sleep 15
    
    # Verify container is now running
    if [ "$(docker ps -q -f ancestor=$image_name)" ]; then
        echo -e "${GREEN}✓ Neo4j is now running.${NC}"
    else
        echo -e "${RED}Warning: Neo4j container may not have started correctly.${NC}"
        echo -e "${YELLOW}Attempting to continue workflow anyway...${NC}"
    fi
fi

# Get the actual container name for later use
container_name=$(docker ps --filter "ancestor=$image_name" --format "{{.Names}}" | head -n 1)
if [ -z "$container_name" ]; then
    container_name="neo4j" # Fallback name if we can't determine the actual name
fi

# Step 2: Process document into graph
echo -e "\n${YELLOW}Step 2: Process document into graph...${NC}"

# List documents in the ./documents/ folder
echo -e "${BLUE}Available documents in ./documents/ folder:${NC}"

# Make sure the documents directory exists
if [ ! -d "./documents" ]; then
    echo -e "${YELLOW}The ./documents/ folder does not exist. Creating it now...${NC}"
    mkdir -p ./documents
    echo -e "${YELLOW}Please add your document files to the ./documents/ folder and run this script again.${NC}"
    exit 1
fi

# Find document files and store in an array
mapfile -t document_files < <(find ./documents -type f -name "*.txt" -o -name "*.pdf" -o -name "*.md" | sort)

# Check if any documents were found
if [ ${#document_files[@]} -eq 0 ]; then
    echo -e "${YELLOW}No document files found in ./documents/ folder.${NC}"
    echo -e "${YELLOW}Would you like to:${NC}"
    echo "1. Enter a custom path to a document"
    echo "2. Exit and add documents to the ./documents/ folder"
    read -p "Selection [1]: " no_docs_option
    no_docs_option=${no_docs_option:-1}
    
    if [ "$no_docs_option" = "1" ]; then
        echo -e "${BLUE}Enter the full path to your document:${NC}"
        read document_path
        if [ ! -f "$document_path" ]; then
            echo -e "${RED}File not found: $document_path. Exiting.${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}Please add your document files to the ./documents/ folder and run this script again.${NC}"
        exit 0
    fi
else
    # Display the documents with numbers
    for i in "${!document_files[@]}"; do
        # Get just the filename without the full path for display
        filename=$(basename "${document_files[$i]}")
        echo "$((i+1)). $filename"
    done
    
    # Option for custom path
    echo "$((${#document_files[@]}+1)). Enter custom path"
    
    # Ask user to select a document
    echo -e "${BLUE}Select a document to process [1]:${NC}"
    read -p "Selection: " document_selection
    document_selection=${document_selection:-1}
    
    # Handle custom path option
    if [ "$document_selection" -eq "$((${#document_files[@]}+1))" ]; then
        echo -e "${BLUE}Enter the full path to your document:${NC}"
        read document_path
        if [ ! -f "$document_path" ]; then
            echo -e "${RED}File not found: $document_path. Exiting.${NC}"
            exit 1
        fi
    else
        # Validate selection
        if [ "$document_selection" -lt 1 ] || [ "$document_selection" -gt "${#document_files[@]}" ]; then
            echo -e "${RED}Invalid selection. Using the first document.${NC}"
            document_selection=1
        fi
        
        # Get the selected document path
        document_path="${document_files[$((document_selection-1))]}"
    fi
fi

# Confirm the selected document
echo -e "${GREEN}Selected document: $document_path${NC}"

echo -e "${BLUE}Select processing options:${NC}"
echo "1. Use adaptive chunking (recommended for most documents)"
echo "2. Standard processing with default chunk size"
echo "3. Custom chunk size and overlap"
read -p "Selection [1]: " chunk_option
chunk_option=${chunk_option:-1}

# Handle custom chunk size option
chunk_size_arg=""
chunk_overlap_arg=""
if [ "$chunk_option" = "3" ]; then
    echo -e "${BLUE}Enter custom chunk size (default is 1000):${NC}"
    read -p "Chunk size: " custom_chunk_size
    if [[ -n "$custom_chunk_size" && "$custom_chunk_size" =~ ^[0-9]+$ ]]; then
        chunk_size_arg="--chunk-size $custom_chunk_size"
    else
        echo -e "${YELLOW}Invalid chunk size, using default.${NC}"
    fi
    
    echo -e "${BLUE}Enter custom chunk overlap (default is 100):${NC}"
    read -p "Chunk overlap: " custom_chunk_overlap
    if [[ -n "$custom_chunk_overlap" && "$custom_chunk_overlap" =~ ^[0-9]+$ ]]; then
        chunk_overlap_arg="--chunk-overlap $custom_chunk_overlap"
    else
        echo -e "${YELLOW}Invalid chunk overlap, using default.${NC}"
    fi
elif [ "$chunk_option" = "1" ]; then
    chunk_arg="--adaptive"
    echo "Using adaptive chunking..."
fi

echo -e "${BLUE}Clear existing graph data?${NC}"
echo "1. Yes, clear existing data (recommended for new documents)"
echo "2. No, preserve existing data (add to existing graph)"
read -p "Selection [1]: " clear_option
clear_option=${clear_option:-1}

# Add verification for clearing existing data
preserve_arg=""
if [ "$clear_option" = "1" ]; then
    echo -e "${YELLOW}WARNING: This will delete all existing data in your Neo4j database.${NC}"
    echo -e "Are you sure you want to continue? Type 'yes' to confirm:"
    read confirmation
    if [[ ! "$confirmation" =~ ^[Yy][Ee][Ss]$ ]]; then
        echo -e "${YELLOW}Operation cancelled. Will preserve existing data instead.${NC}"
        preserve_arg="--preserve"
    else
        echo -e "${YELLOW}Confirmed. Will clear all existing data.${NC}"
    fi
else
    preserve_arg="--preserve"
    echo "Preserving existing graph data..."
fi

# Add parallel processing configuration
echo -e "${BLUE}Enable parallel processing?${NC}"
echo "1. Yes, process in parallel (recommended for faster processing)"
echo "2. No, process sequentially"
read -p "Selection [1]: " parallel_option
parallel_option=${parallel_option:-1}

parallel_arg=""
workers_arg=""
if [ "$parallel_option" = "1" ]; then
    parallel_arg="--parallel"
    
    # Get number of CPU cores for a reasonable default
    if command -v nproc &> /dev/null; then
        cpu_cores=$(nproc)
    elif [ -f /proc/cpuinfo ]; then
        cpu_cores=$(grep -c ^processor /proc/cpuinfo)
    else
        cpu_cores=4  # Default if we can't determine
    fi
    
    # Suggest a reasonable default (75% of cores)
    suggested_workers=$(($cpu_cores * 3 / 4))
    if [ $suggested_workers -lt 1 ]; then
        suggested_workers=1
    fi
    
    echo -e "${BLUE}Number of parallel workers (default: $suggested_workers):${NC}"
    read -p "Workers [$suggested_workers]: " workers
    workers=${workers:-$suggested_workers}
    
    workers_arg="--workers $workers"
    echo "Using parallel processing with $workers workers..."
else
    echo "Using sequential processing..."
fi

# Combine all arguments for the document processing script
script_args="$document_path $chunk_arg $preserve_arg $parallel_arg $workers_arg $chunk_size_arg $chunk_overlap_arg --verbose-extraction"

echo "Running document processor on $document_path..."
echo -e "${BLUE}Command: python cyber-poc_2-langchain-document-to-graph-adaptive.py $script_args${NC}"
python cyber-poc_2-langchain-document-to-graph-adaptive.py $script_args
check_error "Document processing failed"

# Step 3: Create vector store from graph
echo -e "\n${YELLOW}Step 3: Creating vector stores from graph...${NC}"
echo "Listing available node labels in the graph..."

# Select embedding model
echo -e "${BLUE}Select embedding model:${NC}"
echo "1. nomic-embed-text:latest (default, recommended)"
echo "2. all-minilm (faster, less accurate)"
echo "3. Specify another model"
read -p "Selection [1]: " model_option
model_option=${model_option:-1}

model_arg=""
if [ "$model_option" = "1" ]; then
    model_arg="--model nomic-embed-text:latest"
elif [ "$model_option" = "2" ]; then
    model_arg="--model all-minilm"
elif [ "$model_option" = "3" ]; then
    echo -e "${BLUE}Enter model name:${NC}"
    read custom_model
    model_arg="--model $custom_model"
fi

# List available labels
python neo4j_3-langchain-graph-to-vector-store.py --list-labels
check_error "Failed to list labels from Neo4j"

echo -e "\n${BLUE}Select which node types to vectorize:${NC}"
echo "1. Vectorize all node types (recommended)"
echo "2. Select specific node type"
read -p "Selection [1]: " vectorize_option
vectorize_option=${vectorize_option:-1}

if [ "$vectorize_option" = "1" ]; then
    echo "Creating vector stores for all node types..."
    echo -e "${BLUE}Command: python neo4j_3-langchain-graph-to-vector-store.py --all $model_arg --test-query \"test\"${NC}"
    python neo4j_3-langchain-graph-to-vector-store.py --all $model_arg --test-query "test"
    check_error "Vector store creation failed"
else
    echo -e "${BLUE}Enter the node label to vectorize:${NC}"
    read node_label
    echo "Creating vector store for $node_label..."
    echo -e "${BLUE}Command: python neo4j_3-langchain-graph-to-vector-store.py --label $node_label $model_arg --test-query \"test\"${NC}"
    python neo4j_3-langchain-graph-to-vector-store.py --label $node_label $model_arg --test-query "test"
    check_error "Vector store creation failed"
fi

# Step 4: Run RAG Q&A
echo -e "\n${YELLOW}Step 4: Running Hybrid RAG Q&A...${NC}"
echo "Listing available vector indices..."

# List available indices
python neo4j_4-langchain-neo4j-hybrid-RAG.py --list-indices
check_error "Failed to list vector indices"

# Select index
echo -e "\n${BLUE}Enter the index name to use (leave blank to choose from the list):${NC}"
read index_name
index_arg=""
if [ ! -z "$index_name" ]; then
    index_arg="--index $index_name"
fi

# Select LLM
echo -e "${BLUE}Select LLM model for question answering:${NC}"
echo "1. llama3-chatqa:8b (default, recommended)"
echo "2. llama3:8b"
echo "3. Specify another model"
read -p "Selection [1]: " llm_option
llm_option=${llm_option:-1}

llm_arg=""
if [ "$llm_option" = "1" ]; then
    llm_arg="--llm llama3-chatqa:8b"
elif [ "$llm_option" = "2" ]; then
    llm_arg="--llm llama3:8b"
elif [ "$llm_option" = "3" ]; then
    echo -e "${BLUE}Enter LLM model name:${NC}"
    read custom_llm
    llm_arg="--llm $custom_llm"
fi

# Configure temperature
echo -e "${BLUE}Set temperature for LLM responses (0.0-1.0, default: 0.1):${NC}"
read -p "Temperature [0.1]: " temperature
temperature=${temperature:-0.1}
temp_arg="--temperature $temperature"

echo -e "\n${GREEN}Starting interactive Q&A session...${NC}"
echo -e "${BLUE}Command: python neo4j_4-langchain-neo4j-hybrid-RAG.py --interactive $index_arg $llm_arg $temp_arg${NC}"
python neo4j_4-langchain-neo4j-hybrid-RAG.py --interactive $index_arg $llm_arg $temp_arg
check_error "RAG Q&A session failed"

# Step 5: Clean up (optional)
echo -e "\n${YELLOW}Step 5: Clean up (optional)${NC}"
echo -e "Options:"
echo -e "1. Continue with Neo4j running"
echo -e "2. Stop the Neo4j container"
echo -e "3. Stop and remove the Neo4j container"
read -p "Selection [1]: " cleanup_option
cleanup_option=${cleanup_option:-1}

if [ "$cleanup_option" = "2" ]; then
    echo "Stopping Neo4j container ($container_name)..."
    docker stop $container_name
    check_error "Failed to stop container"
    echo -e "${GREEN}✓ Neo4j container stopped${NC}"
elif [ "$cleanup_option" = "3" ]; then
    echo "Stopping and removing Neo4j container ($container_name)..."
    docker stop $container_name
    check_error "Failed to stop container"
    docker rm $container_name
    check_error "Failed to remove container"
    echo -e "${GREEN}✓ Neo4j container stopped and removed${NC}"
fi

echo -e "\n${GREEN}=== WORKFLOW COMPLETE ===${NC}"
echo -e "You now have a functional knowledge graph with vector search capabilities!"