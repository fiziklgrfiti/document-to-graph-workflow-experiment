#!/bin/bash
# neo4j-backup-restore.sh - Workflow for Neo4j database backup and restore

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
echo -e "\n${GREEN}=== NEO4J BACKUP & RESTORE WORKFLOW ===${NC}\n"

# Step 1: Check if Neo4j is running and start if needed
echo -e "${YELLOW}Step 1: Checking Neo4j status...${NC}"
image_name="langchain-examples-neo4j"

# Check if a container with the neo4j image is running
if [ "$(docker ps -q -f ancestor=$image_name)" ]; then
    echo -e "${GREEN}✓ A Neo4j container is already running.${NC}"
else
    # If not running, check if we need to start our docker-compose setup
    echo "No Neo4j container found running. Starting docker-compose..."
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

# Main menu for backup or restore
echo -e "\n${BLUE}Select an operation:${NC}"
echo "1. Backup Neo4j database"
echo "2. Restore Neo4j database"
echo "3. List available backups"
echo "4. Exit"
read -p "Selection [1]: " operation
operation=${operation:-1}

case $operation in
    1)
        # Backup operation
        echo -e "\n${YELLOW}Step 2: Backing up Neo4j database...${NC}"
        echo -e "Running backup script..."
        
        python neo4j_backup.py --container $container_name
        check_error "Backup failed"
        
        echo -e "\n${GREEN}Backup completed successfully!${NC}"
        ;;
        
    2)
        # Restore operation
        echo -e "\n${YELLOW}Step 2: Restoring Neo4j database...${NC}"
        
        # First list available backups
        echo -e "Available backups:"
        python neo4j_restore.py --container $container_name --list
        check_error "Failed to list backups"
        
        # Ask for specific backup or use latest
        echo -e "\n${BLUE}Do you want to:${NC}"
        echo "1. Restore the most recent backup"
        echo "2. Select a specific backup"
        read -p "Selection [1]: " restore_option
        restore_option=${restore_option:-1}
        
        if [ "$restore_option" = "1" ]; then
            # Use the most recent backup
            python neo4j_restore.py --container $container_name
            check_error "Restore failed"
        else
            # Let the user select from the list
            python neo4j_restore.py --container $container_name
            check_error "Restore failed"
        fi
        
        echo -e "\n${GREEN}Restore completed successfully!${NC}"
        echo -e "${YELLOW}Note: To restore vector indices, you'll need to run:${NC}"
        echo -e "python neo4j_3-langchain-graph-to-vector-store.py --all"
        ;;
        
    3)
        # List available backups
        echo -e "\n${YELLOW}Listing available backups...${NC}"
        python neo4j_restore.py --container $container_name --list
        ;;
        
    4)
        # Exit
        echo -e "\n${GREEN}Exiting workflow.${NC}"
        exit 0
        ;;
        
    *)
        echo -e "${RED}Invalid selection.${NC}"
        exit 1
        ;;
esac

# Step 3: Additional options after backup/restore
if [ "$operation" = "1" ] || [ "$operation" = "2" ]; then
    echo -e "\n${YELLOW}Step 3: Additional options...${NC}"
    
    echo -e "\n${BLUE}Would you like to:${NC}"
    echo "1. Continue with Neo4j running"
    echo "2. Stop the Neo4j container"
    echo "3. Run the Neo4j workflow script (neo4j-5-workflow.sh)"
    read -p "Selection [1]: " cleanup_option
    cleanup_option=${cleanup_option:-1}
    
    if [ "$cleanup_option" = "2" ]; then
        echo "Stopping Neo4j container ($container_name)..."
        docker stop $container_name
        check_error "Failed to stop container"
        echo -e "${GREEN}✓ Neo4j container stopped${NC}"
    elif [ "$cleanup_option" = "3" ]; then
        echo "Running Neo4j workflow script..."
        ./neo4j-5-workflow.sh
    fi
fi

echo -e "\n${GREEN}=== WORKFLOW COMPLETE ===${NC}"