#!/bin/bash
# neo4j-entity-validation-workflow.sh - Workflow for validating entities against documents

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
echo -e "\n${GREEN}=== NEO4J ENTITY VALIDATION WORKFLOW ===${NC}\n"

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

# Step 2: Run Entity Validation
echo -e "\n${YELLOW}Step 2: Running Entity Validation...${NC}"

# Offer to back up the database first
echo -e "${BLUE}Would you like to backup the Neo4j database before validation? (y/n):${NC}"
read -p "Backup database [y]: " backup_option
backup_option=${backup_option:-y}

if [[ "$backup_option" =~ ^[Yy]$ ]]; then
    # Check if backup script exists
    if [ -f "./neo4j_backup.py" ]; then
        echo -e "\n${GREEN}Backing up Neo4j database...${NC}"
        python neo4j_backup.py --container $container_name
        check_error "Backup failed"
        echo -e "${GREEN}✓ Database backup completed${NC}"
    else
        echo -e "${YELLOW}Backup script not found. Skipping backup.${NC}"
        echo -e "${YELLOW}It is recommended to implement a backup solution before proceeding with entity deletion.${NC}"
        
        # Confirm to continue without backup
        echo -e "${RED}Continue without backup? This is risky as entities may be permanently deleted. (y/n):${NC}"
        read -p "Continue [n]: " continue_option
        continue_option=${continue_option:-n}
        
        if [[ ! "$continue_option" =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}Operation cancelled.${NC}"
            exit 0
        fi
    fi
fi

# Configure semantic analysis option
echo -e "${BLUE}Use semantic analysis (LLM) to validate entities that don't match by name? (y/n):${NC}"
echo -e "${YELLOW}Note: Semantic analysis is slower but more thorough${NC}"
read -p "Use semantic analysis [y]: " semantic_option
semantic_option=${semantic_option:-y}

semantic_arg=""
if [[ "$semantic_option" =~ ^[Yy]$ ]]; then
    semantic_arg="--semantic"
    
    # Select LLM model
    echo -e "${BLUE}Select LLM model for semantic analysis:${NC}"
    echo "1. gemma3:4b (default, fastest)"
    echo "2. llama3.1:latest (better quality)"
    echo "3. gemma3:12b (fallback)"
    echo "4. Specify another model"
    read -p "Selection [1]: " model_option
    model_option=${model_option:-1}
    
    model_arg=""
    if [ "$model_option" = "1" ]; then
        model_arg="--model gemma3:4b"
    elif [ "$model_option" = "2" ]; then
        model_arg="--model llama3.1:latest"
    elif [ "$model_option" = "3" ]; then
        model_arg="--model gemma3:12b"
    elif [ "$model_option" = "4" ]; then
        echo -e "${BLUE}Enter LLM model name:${NC}"
        read custom_model
        model_arg="--model $custom_model"
    fi
fi

# Select operation mode
echo -e "\n${BLUE}Select operation mode:${NC}"
echo "1. Validate existing entities (find hallucinations)"
echo "2. Discover new entities"
echo "3. Both validate and discover"
read -p "Select operation mode (1-3) [1]: " operation_mode
operation_mode=${operation_mode:-1}

# Configure discovery options
discovery_arg=""
max_entities_arg=""
if [ "$operation_mode" = "2" ] || [ "$operation_mode" = "3" ]; then
    discovery_arg="--discover"
    
    # Configure max entities
    echo -e "${BLUE}Maximum number of new entities to discover:${NC}"
    read -p "Max entities [5]: " max_entities
    max_entities=${max_entities:-5}
    max_entities_arg="--max-entities $max_entities"
fi

# Run the appropriate script with the right arguments
if [ "$operation_mode" = "1" ]; then
    # Validation only
    command_args="--interactive $semantic_arg $model_arg"
elif [ "$operation_mode" = "2" ]; then
    # Discovery only
    command_args="--interactive $semantic_arg $model_arg $discovery_arg $max_entities_arg"
else
    # Both validation and discovery
    command_args="--interactive $semantic_arg $model_arg $discovery_arg $max_entities_arg"
fi

echo -e "${BLUE}Command: python neo4j_8-entity-validation.py $command_args${NC}"
python neo4j_8-entity-validation.py $command_args
check_error "Entity operation failed"

# Step 3: Ask if they want to run vector store update
echo -e "\n${YELLOW}Step 3: Update vector indices (optional)...${NC}"
echo -e "${BLUE}Would you like to update vector indices now? (y/n):${NC}"
read -p "Update vector indices [y]: " update_option
update_option=${update_option:-y}

if [[ "$update_option" =~ ^[Yy]$ ]]; then
    echo -e "\n${GREEN}Updating vector indices...${NC}"
    
    # List available labels
    python neo4j_3-langchain-graph-to-vector-store.py --list-labels
    
    echo -e "${BLUE}Update vectors for all entity types or a specific label?${NC}"
    echo "1. All entity types"
    echo "2. Specific entity type"
    read -p "Selection [1]: " index_option
    index_option=${index_option:-1}
    
    if [ "$index_option" = "1" ]; then
        # Update all indices
        echo -e "${BLUE}Command: python neo4j_3-langchain-graph-to-vector-store.py --all --model nomic-embed-text:latest${NC}"
        python neo4j_3-langchain-graph-to-vector-store.py --all --model nomic-embed-text:latest
    else
        echo -e "${BLUE}Enter the node label to update vector indices for:${NC}"
        read node_label
        
        echo -e "${BLUE}Command: python neo4j_3-langchain-graph-to-vector-store.py --label $node_label --model nomic-embed-text:latest${NC}"
        python neo4j_3-langchain-graph-to-vector-store.py --label $node_label --model nomic-embed-text:latest
    fi
    
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}Warning: Vector index update failed, but entity validation was successful.${NC}"
    else
        echo -e "${GREEN}✓ Vector indices updated successfully${NC}"
    fi
fi

# Step 4: Run hybrid RAG for testing (optional)
echo -e "\n${YELLOW}Step 4: Test with Hybrid RAG (optional)...${NC}"
echo -e "${BLUE}Would you like to run a test query using Hybrid RAG? (y/n):${NC}"
read -p "Run test query [n]: " rag_option
rag_option=${rag_option:-n}

if [[ "$rag_option" =~ ^[Yy]$ ]]; then
    echo -e "\n${GREEN}Starting Hybrid RAG...${NC}"
    
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
        echo -e "${YELLOW}Warning: RAG test failed, but entity validation was successful.${NC}"
    fi
fi

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

# Summary
echo -e "\n${GREEN}=== WORKFLOW SUMMARY ===${NC}"
echo -e "Entity validation &/or discovery completed successfully"
echo -e "Check the validation reports in the 'validation_reports' directory"
echo -e "\n${GREEN}=== WORKFLOW COMPLETE ===${NC}"