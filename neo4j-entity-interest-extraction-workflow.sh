#!/bin/bash
# neo4j-entity-extraction-workflow.sh - Workflow for entity-focused extraction from documents

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
echo -e "\n${GREEN}=== NEO4J ENTITY-FOCUSED EXTRACTION WORKFLOW ===${NC}\n"

# Step 1: Check if Neo4j is running and start if needed
echo -e "${YELLOW}Step 1: Checking Neo4j status...${NC}"
image_name="langchain-examples-neo4j"

# Check if a container with the neo4j image is running
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

# Step 2: Select a document to process
echo -e "\n${YELLOW}Step 2: Select a document to process...${NC}"

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

# Step 3: Configure LLM model
echo -e "\n${YELLOW}Step 3: Configure LLM model...${NC}"

# Select LLM model
echo -e "${BLUE}Select LLM model for entity extraction:${NC}"
echo "1. gemma3:12b (default, recommended)"
echo "2. llama3:latest"
echo "3. mistral:7b"
echo "4. Specify another model"
read -p "Selection [1]: " model_option
model_option=${model_option:-1}

llm_model=""
if [ "$model_option" = "1" ]; then
    llm_model="gemma3:12b"
elif [ "$model_option" = "2" ]; then
    llm_model="llama3:latest"
elif [ "$model_option" = "3" ]; then
    llm_model="mistral:7b"
elif [ "$model_option" = "4" ]; then
    echo -e "${BLUE}Enter LLM model name:${NC}"
    read custom_model
    llm_model="$custom_model"
fi

# Configure temperature
echo -e "${BLUE}Set temperature for LLM responses (0.0-1.0, default: 0.1):${NC}"
read -p "Temperature [0.1]: " temperature
temperature=${temperature:-0.1}

# Step 4: Configure chunking parameters
echo -e "\n${YELLOW}Step 4: Configure document chunking parameters...${NC}"

echo -e "${BLUE}Select document chunking options:${NC}"
echo "1. Use default chunking parameters (size: 1000, overlap: 200)"
echo "2. Custom chunk size and overlap"
read -p "Selection [1]: " chunk_option
chunk_option=${chunk_option:-1}

chunk_size_arg=""
chunk_overlap_arg=""
if [ "$chunk_option" = "2" ]; then
    echo -e "${BLUE}Enter chunk size (default is 1000):${NC}"
    read -p "Chunk size: " custom_chunk_size
    if [[ -n "$custom_chunk_size" && "$custom_chunk_size" =~ ^[0-9]+$ ]]; then
        chunk_size_arg="--chunk-size $custom_chunk_size"
    else
        echo -e "${YELLOW}Invalid chunk size, using default (1000).${NC}"
        chunk_size_arg="--chunk-size 1000"
    fi
    
    echo -e "${BLUE}Enter chunk overlap (default is 200):${NC}"
    read -p "Chunk overlap: " custom_chunk_overlap
    if [[ -n "$custom_chunk_overlap" && "$custom_chunk_overlap" =~ ^[0-9]+$ ]]; then
        chunk_overlap_arg="--chunk-overlap $custom_chunk_overlap"
    else
        echo -e "${YELLOW}Invalid chunk overlap, using default (200).${NC}"
        chunk_overlap_arg="--chunk-overlap 200"
    fi
else
    chunk_size_arg="--chunk-size 1000"
    chunk_overlap_arg="--chunk-overlap 200"
fi

# Step 5: Select processing mode
echo -e "\n${YELLOW}Step 5: Select processing mode...${NC}"
echo -e "${BLUE}How would you like to process entities?${NC}"
echo "1. Process a specific entity (interactive selection)"
echo "2. Process an entity type (all entities of that type)"
echo "3. Process a single entity by ID (non-interactive)"
read -p "Selection [1]: " processing_mode
processing_mode=${processing_mode:-1}

run_vector_store_update=false
output_dir="extracted_entities"
entity_count=0
run_all=false

# Process based on mode selection
if [ "$processing_mode" = "1" ]; then
    # Interactive entity selection mode
    echo -e "\n${GREEN}Running interactive entity selection mode...${NC}"
    command_args="--interactive --document $document_path --model $llm_model --temperature $temperature $chunk_size_arg $chunk_overlap_arg --output-dir $output_dir"
    
    echo -e "${BLUE}Command: python neo4j_7-neo4j-entity-focused-extraction.py $command_args${NC}"
    python neo4j_7-neo4j-entity-focused-extraction.py $command_args
    check_error "Entity extraction failed"
    
    entity_count=1
    
elif [ "$processing_mode" = "2" ]; then
    # Process all entities of a specific type
    # Get entity types from the list
    echo -e "\n${GREEN}Listing entity types in the graph...${NC}"
    python neo4j_7-neo4j-entity-focused-extraction.py --list-entities
    
    # Ask for entity type selection - directly ask for the label
    echo -e "${BLUE}Enter the entity type label (e.g., 'Unit', 'weapon'):${NC}"
    read entity_type
    
    if [ -z "$entity_type" ]; then
        echo -e "${RED}No entity type provided. Exiting.${NC}"
        exit 1
    fi
    
    # List entities of the selected type
    echo -e "\n${GREEN}Listing entities of type '$entity_type'...${NC}"
    python neo4j_7-neo4j-entity-focused-extraction.py --list-entities --entity-type "$entity_type"

    
    # Confirm processing all entities of this type
    echo -e "${YELLOW}WARNING: This will process all entities of type '$entity_type'.${NC}"
    echo -e "Are you sure you want to continue? Type 'yes' to confirm:"
    read confirmation
    if [[ ! "$confirmation" =~ ^[Yy][Ee][Ss]$ ]]; then
        echo -e "${YELLOW}Operation cancelled.${NC}"
        exit 0
    fi
    
    # Extract entity IDs from the output
    echo -e "${YELLOW}WARNING: This will process all entities of type '$entity_type'.${NC}"
    echo -e "Are you sure you want to continue? Type 'yes' to confirm:"
    read confirmation
    if [[ ! "$confirmation" =~ ^[Yy][Ee][Ss]$ ]]; then
        echo -e "${YELLOW}Operation cancelled.${NC}"
        exit 0
    fi
    
    # Get entity IDs by parsing the output
    echo -e "\n${BLUE}Extracting entity IDs for processing...${NC}"
    
    # Temporarily save the output to a file
    tmp_file=$(mktemp)
    python neo4j_7-neo4j-entity-focused-extraction.py --list-entities --entity-type "$entity_type" > "$tmp_file" 2>&1
    
    # Extract IDs using a simpler approach
    entity_ids=()
    while IFS= read -r line; do
        # Look for ID pattern using grep instead of bash regex
        if echo "$line" | grep -q "ID:"; then
            # Extract the ID part
            id_part=$(echo "$line" | grep -o "ID: [^)]*" | sed 's/ID: //')
            if [ ! -z "$id_part" ]; then
                entity_ids+=("$id_part")
            fi
        fi
    done < "$tmp_file"
    
    # Clean up
    rm "$tmp_file"
    
    # Alternative ID extraction with grep
    if [ ${#entity_ids[@]} -eq 0 ]; then
        echo -e "${YELLOW}Trying alternative method to extract entity IDs...${NC}"
        mapfile -t entity_ids < <(grep -o "ID: [^ )]*" "$tmp_file" | sed 's/ID: //')
        
        if [ ${#entity_ids[@]} -eq 0 ]; then
            echo -e "${RED}No entity IDs found for type '$entity_type'.${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}Found ${#entity_ids[@]} entities to process.${NC}"
    
    # Process each entity
    echo -e "\n${GREEN}Processing all entities of type '$entity_type'...${NC}"
    for entity_id in "${entity_ids[@]}"; do
        echo -e "\n${BLUE}Processing entity ID: $entity_id${NC}"
        command_args="--entity-id $entity_id --document $document_path --model $llm_model --temperature $temperature $chunk_size_arg $chunk_overlap_arg --output-dir $output_dir"
        
        echo -e "${BLUE}Command: python neo4j_7-neo4j-entity-focused-extraction.py $command_args${NC}"
        python neo4j_7-neo4j-entity-focused-extraction.py $command_args
        
        # Don't exit on error, just continue with next entity
        if [ $? -ne 0 ]; then
            echo -e "${YELLOW}Warning: Processing failed for entity ID: $entity_id, continuing with next entity.${NC}"
        else
            entity_count=$((entity_count + 1))
        fi
    done
    
    run_vector_store_update=true
    run_all=true
    
elif [ "$processing_mode" = "3" ]; then
    # Non-interactive mode with specific entity ID
    echo -e "\n${BLUE}Enter the entity ID to process:${NC}"
    read entity_id
    
    command_args="--entity-id $entity_id --document $document_path --model $llm_model --temperature $temperature $chunk_size_arg $chunk_overlap_arg --output-dir $output_dir"
    
    echo -e "${BLUE}Command: python neo4j_7-neo4j-entity-focused-extraction.py $command_args${NC}"
    python neo4j_7-neo4j-entity-focused-extraction.py $command_args
    check_error "Entity extraction failed"
    
    entity_count=1
fi

# Step 6: Update vector indices (optional)
echo -e "\n${YELLOW}Step 6: Update vector indices (optional)...${NC}"

if [ $entity_count -eq 0 ]; then
    echo -e "${YELLOW}No entities were processed. Skipping vector index update.${NC}"
else
    if [ "$run_all" = true ] || [ "$run_vector_store_update" = true ]; then
        update_option="y"
        echo -e "${GREEN}Auto-updating vector indices for processed entities...${NC}"
    else
        echo -e "${BLUE}Would you like to update vector indices for the processed entities? (y/n):${NC}"
        read -p "Update vector indices [y]: " update_option
        update_option=${update_option:-y}
    fi
    
    if [[ "$update_option" =~ ^[Yy]$ ]]; then
        echo -e "\n${GREEN}Updating vector indices...${NC}"
        
        if [ "$run_all" = true ]; then
            # Update all indices
            echo -e "${BLUE}Command: python neo4j_3-langchain-graph-to-vector-store.py --all --model nomic-embed-text:latest${NC}"
            python neo4j_3-langchain-graph-to-vector-store.py --all --model nomic-embed-text:latest
        else
            # List available labels
            python neo4j_3-langchain-graph-to-vector-store.py --list-labels
            
            echo -e "${BLUE}Enter the node label to update vector indices for:${NC}"
            read node_label
            
            echo -e "${BLUE}Command: python neo4j_3-langchain-graph-to-vector-store.py --label $node_label --model nomic-embed-text:latest${NC}"
            python neo4j_3-langchain-graph-to-vector-store.py --label $node_label --model nomic-embed-text:latest
        fi
        
        if [ $? -ne 0 ]; then
            echo -e "${YELLOW}Warning: Vector index update failed, but entity extraction was successful.${NC}"
        else
            echo -e "${GREEN}✓ Vector indices updated successfully${NC}"
        fi
    fi
fi

# Step 7: Run RAG Q&A (optional)
echo -e "\n${YELLOW}Step 7: Run RAG Q&A (optional)...${NC}"

if [ $entity_count -eq 0 ]; then
    echo -e "${YELLOW}No entities were processed. Skipping RAG Q&A.${NC}"
else
    echo -e "${BLUE}Would you like to run the Hybrid RAG Q&A? (y/n):${NC}"
    read -p "Run Q&A [y]: " qa_option
    qa_option=${qa_option:-y}
    
    if [[ "$qa_option" =~ ^[Yy]$ ]]; then
        echo -e "\n${GREEN}Starting Hybrid RAG Q&A...${NC}"
        
        # List available indices
        python neo4j_4-langchain-neo4j-hybrid-RAG.py --list-indices
        
        echo -e "${BLUE}Enter the index name to use (leave blank to choose from list):${NC}"
        read index_name
        index_arg=""
        if [ ! -z "$index_name" ]; then
            index_arg="--index $index_name"
        fi
        
        echo -e "${BLUE}Command: python neo4j_4-langchain-neo4j-hybrid-RAG.py --interactive $index_arg${NC}"
        python neo4j_4-langchain-neo4j-hybrid-RAG.py --interactive $index_arg
        
        if [ $? -ne 0 ]; then
            echo -e "${YELLOW}Warning: RAG Q&A failed, but entity extraction was successful.${NC}"
        fi
    fi
fi

# Step 8: Run enhanced hybrid RAG (optional)
echo -e "\n${YELLOW}Step 8: Run Enhanced Hybrid RAG (optional)...${NC}"

if [ $entity_count -eq 0 ]; then
    echo -e "${YELLOW}No entities were processed. Skipping Enhanced Hybrid RAG.${NC}"
else
    echo -e "${BLUE}Would you like to run the Enhanced Hybrid RAG? (y/n):${NC}"
    read -p "Run Enhanced RAG [n]: " erag_option
    erag_option=${erag_option:-n}
    
    if [[ "$erag_option" =~ ^[Yy]$ ]]; then
        echo -e "\n${GREEN}Starting Enhanced Hybrid RAG...${NC}"
        
        # List available indices
        python neo4j_6-enhanced-hybrid-RAG.py --list-indices
        
        echo -e "${BLUE}Enter the index name to use (leave blank to choose from list):${NC}"
        read index_name
        index_arg=""
        if [ ! -z "$index_name" ]; then
            index_arg="--index $index_name"
        fi
        
        echo -e "${BLUE}Command: python neo4j_6-enhanced-hybrid-RAG.py --interactive $index_arg${NC}"
        python neo4j_6-enhanced-hybrid-RAG.py --interactive $index_arg
        
        if [ $? -ne 0 ]; then
            echo -e "${YELLOW}Warning: Enhanced Hybrid RAG failed, but entity extraction was successful.${NC}"
        fi
    fi
fi

# Step 9: Clean up (optional)
echo -e "\n${YELLOW}Step 9: Clean up (optional)${NC}"
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

# Summary
echo -e "\n${GREEN}=== WORKFLOW SUMMARY ===${NC}"
echo -e "Document processed: $(basename $document_path)"
echo -e "Entities processed: $entity_count"
if [ $entity_count -gt 0 ]; then
    echo -e "Extraction results saved to: $output_dir/"
fi
echo -e "\n${GREEN}=== WORKFLOW COMPLETE ===${NC}"