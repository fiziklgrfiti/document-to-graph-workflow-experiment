#!/bin/bash
# neo4j-entity-duplicate-detection-workflow.sh - Workflow for entity duplicate detection and resolution

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
echo -e "\n${GREEN}=== NEO4J ENTITY DUPLICATE DETECTION WORKFLOW ===${NC}\n"

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

# Step 2: Offer to back up the database first
echo -e "\n${YELLOW}Step 2: Database Backup (Recommended)${NC}"
echo -e "${BLUE}Would you like to backup the Neo4j database before duplicate detection? (y/n):${NC}"
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

# Step 3: Select LLM model
echo -e "\n${YELLOW}Step 3: Select LLM model${NC}"
echo -e "${BLUE}Select LLM model for duplicate detection:${NC}"
echo "1. llama3.1:latest (default, recommended)"
echo "2. gemma3:12b (good alternative)"
echo "3. gemma3:4b (faster, less accurate)"
echo "4. deepseek-r1:8b (slower, provides verbose chain of thought)"
echo "5. Specify another model"
read -p "Selection [1]: " model_option
model_option=${model_option:-1}

model_arg=""
if [ "$model_option" = "1" ]; then
    model_arg="--model llama3.1:latest"
elif [ "$model_option" = "2" ]; then
    model_arg="--model gemma3:12b"
elif [ "$model_option" = "3" ]; then
    model_arg="--model gemma3:4b"
elif [ "$model_option" = "4" ]; then
    model_arg="--model deepseek-r1:8b"
elif [ "$model_option" = "5" ]; then
    echo -e "${BLUE}Enter LLM model name:${NC}"
    read custom_model
    model_arg="--model $custom_model"
fi

# Configure temperature
echo -e "${BLUE}Set temperature for LLM responses (0.0-1.0, default: 0.1):${NC}"
read -p "Temperature [0.1]: " temperature
temperature=${temperature:-0.1}
temp_arg="--temperature $temperature"

# Step 4: Select operation mode
echo -e "\n${YELLOW}Step 4: Select operation mode${NC}"
echo -e "${BLUE}What would you like to analyze for duplicates?${NC}"
echo "1. Entity types (labels) - Find duplicate entity types"
echo "2. Entities of a specific type - Find duplicate entities within one category"
echo "3. All entities - Find duplicates across all entity types"
echo "4. Load and execute a previously saved resolution plan"
read -p "Selection [1]: " operation_mode
operation_mode=${operation_mode:-1}

operation_args=""
if [ "$operation_mode" = "1" ]; then
    operation_args="--analyze-labels"
elif [ "$operation_mode" = "2" ]; then
    # List available entity types
    echo -e "\n${BLUE}Listing available entity types...${NC}"
    python neo4j_9-entity-duplicate-detection.py --interactive --verbose 2>&1 | grep -A 50 "Available entity types:" | head -20
    
    echo -e "\n${BLUE}Enter the entity type to analyze:${NC}"
    read entity_type
    
    if [ -z "$entity_type" ]; then
        echo -e "${RED}No entity type specified.${NC}"
        exit 1
    fi
    
    operation_args="--entity-type $entity_type"
elif [ "$operation_mode" = "3" ]; then
    operation_args="--interactive"
elif [ "$operation_mode" = "4" ]; then
    # List available resolution plans
    resolution_dir="resolution_plans"
    if [ -d "$resolution_dir" ]; then
        echo -e "\n${BLUE}Available resolution plans:${NC}"
        ls -lt $resolution_dir/*.json | head -10
    else
        echo -e "${RED}No resolution plans directory found.${NC}"
        exit 1
    fi
    
    echo -e "\n${BLUE}Enter the path to the resolution plan:${NC}"
    read plan_path
    
    if [ ! -f "$plan_path" ]; then
        echo -e "${RED}Resolution plan not found: $plan_path${NC}"
        exit 1
    fi
    
    operation_args="--load-plan $plan_path"
else
    echo -e "${RED}Invalid selection.${NC}"
    exit 1
fi

# Step 5: Run the duplicate detection
echo -e "\n${YELLOW}Step 5: Running duplicate detection...${NC}"
echo -e "${BLUE}Command: python neo4j_9-entity-duplicate-detection.py --container $container_name $model_arg $temp_arg $operation_args${NC}"

# Run the command with container name and user-selected options
python neo4j_9-entity-duplicate-detection.py --container $container_name $model_arg $temp_arg $operation_args
check_error "Duplicate detection failed"

if [ "$operation_mode" = "1" ] || [ "$operation_mode" = "2" ]; then
    # Only for entity types or specific entity analysis
    latest_plan=$(ls -t resolution_plans/*.json 2>/dev/null | head -1)
    
    if [ -n "$latest_plan" ] && [ -f "$latest_plan" ]; then
        echo -e "\n${YELLOW}Resolution plan created: ${latest_plan}${NC}"
        echo -e "\n${BLUE}Would you like to execute this resolution plan now? (y/n):${NC}"
        read -p "Execute plan [y]: " execute_option
        execute_option=${execute_option:-y}
        
        if [[ "$execute_option" =~ ^[Yy]$ ]]; then
            # Ask for backup
            echo -e "\n${BLUE}Create a database backup before execution? (recommended) (y/n):${NC}"
            read -p "Backup [y]: " exec_backup
            exec_backup=${exec_backup:-y}
            
            # Pass options to the Python script
            backup_arg=""
            if [[ "$exec_backup" =~ ^[Yy]$ ]]; then
                backup_arg="--backup"
            fi
            
            echo -e "\n${YELLOW}Executing resolution plan...${NC}"
            echo -e "${BLUE}Command: python neo4j_9-entity-duplicate-detection.py --container $container_name --load-plan $latest_plan --execute $backup_arg${NC}"
            
            # Add --execute flag to actually execute the plan
            python neo4j_9-entity-duplicate-detection.py --container $container_name --load-plan $latest_plan --execute $backup_arg
            
            if [ $? -ne 0 ]; then
                echo -e "${RED}❌ Resolution plan execution failed${NC}"
            else
                echo -e "${GREEN}✓ Resolution plan execution completed${NC}"
            fi
        else
            echo -e "${YELLOW}Resolution plan created but not executed.${NC}"
            echo -e "${YELLOW}You can execute it later using option 4 (Load and execute a previously saved resolution plan).${NC}"
        fi
    fi
fi

# Step 6: Clean up (optional)
echo -e "\n${YELLOW}Step 6: Clean up (optional)${NC}"
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

# Step 7: Next steps (vector store update if needed)
echo -e "\n${YELLOW}Step 7: Next steps${NC}"
if [ "$operation_mode" != "4" ]; then  # Only ask for vector update if not just loading a plan
    echo -e "${BLUE}Would you like to update vector indices after the changes? (y/n):${NC}"
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
            echo -e "${YELLOW}Warning: Vector index update failed, but entity changes were successful.${NC}"
        else
            echo -e "${GREEN}✓ Vector indices updated successfully${NC}"
        fi
    fi
fi

# Summary
echo -e "\n${GREEN}=== WORKFLOW SUMMARY ===${NC}"
echo -e "Entity duplicate detection and resolution completed"
echo -e "Check the resolution plans in the 'resolution_plans' directory"
echo -e "\n${GREEN}=== WORKFLOW COMPLETE ===${NC}"