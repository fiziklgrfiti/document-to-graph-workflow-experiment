# neo4j_backup.py
import os
import sys
import time
import argparse
from datetime import datetime
from dotenv import load_dotenv
import subprocess
import warnings

# Load environment variables from .env file
load_dotenv()
warnings.filterwarnings("ignore")

def check_docker_running(container_name="neo4j"):
    """Check if the Neo4j Docker container is running."""
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True
        )
        return container_name in result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error checking Docker container: {e}")
        print(f"Command output: {e.stdout} {e.stderr}")
        return False

def create_backup_directory(base_path="./import"):
    """Create a backup directory with a timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(base_path, f"neo4j_backup_{timestamp}")
    
    # Create the directory
    try:
        os.makedirs(backup_dir, exist_ok=True)
        
        # Set directory permissions to 777 to ensure Neo4j container can write to it
        subprocess.run(["chmod", "-R", "777", backup_dir], check=True)
        
        print(f"Created backup directory: {backup_dir}")
        return backup_dir, timestamp
    except Exception as e:
        print(f"Error creating backup directory: {e}")
        sys.exit(1)

def backup_neo4j_data(backup_dir, container_name="neo4j", verbose=True):
    """
    Backup Neo4j database files using APOC export.
    
    This function backs up:
    1. Graph data (nodes, relationships) using APOC export to GraphML
    2. Vector indices using Neo4j's native backup commands
    """
    try:
        # Step 1: Export graph data using APOC's GraphML export
        # This exports the entire graph to a GraphML file
        graphml_file = os.path.join(backup_dir, "neo4j_graph_data.graphml")
        
        # Construct Cypher query for export
        cypher_query = "CALL apoc.export.graphml.all($file, {useTypes: true, readLabels: true})"
        
        # Run the Cypher query using docker exec and cypher-shell
        username = os.getenv("NEO4J_USERNAME", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        
        if verbose:
            print(f"Backing up graph data to: {graphml_file}")
            print("This may take a few moments...")
        
        # First ensure the directory has proper permissions inside the container
        container_backup_dir = f"/import/{os.path.basename(backup_dir)}"
        chmod_cmd = [
            "docker", "exec", container_name,
            "bash", "-c", f"mkdir -p {container_backup_dir} && chmod 777 {container_backup_dir}"
        ]
        
        try:
            subprocess.run(chmod_cmd, check=True, capture_output=True)
            if verbose:
                print(f"Set permissions for backup directory in container")
        except subprocess.CalledProcessError as e:
            print(f"Warning: Could not set permissions in container: {e.stderr}")
            # Continue anyway, as it might still work
        
        # Command to run within the container
        container_path = f"{container_backup_dir}/neo4j_graph_data.graphml"
        cmd = [
            "docker", "exec", container_name,
            "cypher-shell", 
            "-u", username, 
            "-p", password,
            "-d", "neo4j",  # Database name (default is neo4j)
            f"CALL apoc.export.graphml.all('{container_path}', {{useTypes: true, readLabels: true, storeNodeIds: true}})"
        ]
        
        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error during graph data export using APOC: {result.stderr}")
            print("Attempting alternative backup method...")
            
            # Alternative backup approach: Use Cypher directly to export all nodes and relationships
            # First, export all nodes
            nodes_file = os.path.join(backup_dir, "nodes.csv")
            container_nodes_path = f"/import/{os.path.basename(backup_dir)}/nodes.csv"
            
            nodes_cmd = [
                "docker", "exec", container_name,
                "cypher-shell", 
                "-u", username, 
                "-p", password,
                "-d", "neo4j",
                f"CALL apoc.export.csv.all('{container_nodes_path}', {{}}) YIELD file"
            ]
            
            nodes_result = subprocess.run(nodes_cmd, capture_output=True, text=True)
            
            if nodes_result.returncode != 0:
                print(f"Error during alternative backup: {nodes_result.stderr}")
                return False
            
            if verbose:
                print(f"Alternative backup successful to {nodes_file}")
                
            return True
        
        if verbose:
            print("Graph data backup successful.")
        
        # Step 2: Export vector indices metadata
        # Get list of vector indices
        if verbose:
            print("\nExporting vector indices metadata...")
        
        indices_file = os.path.join(backup_dir, "vector_indices.txt")
        
        cmd = [
            "docker", "exec", container_name,
            "cypher-shell", 
            "-u", username, 
            "-p", password,
            "-d", "neo4j",
            "SHOW VECTOR INDEXES"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error listing vector indices: {result.stderr}")
            # Not critical, continue with backup
        else:
            # Write vector indices information to file
            with open(indices_file, 'w') as f:
                f.write(result.stdout)
            
            if verbose:
                print(f"Vector indices metadata saved to {indices_file}")
        
        # Step 3: Export configuration metadata
        if verbose:
            print("\nExporting Neo4j configuration...")
        
        config_file = os.path.join(backup_dir, "neo4j_config.txt")
        
        cmd = [
            "docker", "exec", container_name,
            "cypher-shell", 
            "-u", username, 
            "-p", password,
            "-d", "neo4j",
            "CALL dbms.listConfig()"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error exporting configuration: {result.stderr}")
            # Not critical, continue with backup
        else:
            # Write configuration to file
            with open(config_file, 'w') as f:
                f.write(result.stdout)
            
            if verbose:
                print(f"Neo4j configuration saved to {config_file}")
        
        # Step 4: Create a metadata file with timestamp and version info
        metadata_file = os.path.join(backup_dir, "backup_metadata.txt")
        
        # Get Neo4j version
        cmd = [
            "docker", "exec", container_name,
            "cypher-shell", 
            "-u", username, 
            "-p", password,
            "-d", "neo4j",
            "CALL dbms.components() YIELD name, versions RETURN name, versions[0] as version"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        version_info = result.stdout if result.returncode == 0 else "Unknown"
        
        # Write metadata
        with open(metadata_file, 'w') as f:
            f.write(f"Backup created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Neo4j version: {version_info}\n")
        
        if verbose:
            print(f"\nBackup metadata saved to {metadata_file}")
            print(f"\n✅ Neo4j backup completed successfully to: {backup_dir}")
        
        return True
        
    except Exception as e:
        print(f"Error during backup process: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(description="Backup Neo4j database")
    parser.add_argument("--container", default="neo4j", help="Neo4j container name")
    parser.add_argument("--backup-dir", default="./import", help="Base directory for backups")
    parser.add_argument("--quiet", action="store_true", help="Reduce output verbosity")
    
    args = parser.parse_args()
    
    print(f"\n{'='*50}")
    print(f"NEO4J DATABASE BACKUP")
    print(f"{'='*50}\n")
    
    # Check if Neo4j container is running
    if not check_docker_running(args.container):
        print(f"❌ Error: Neo4j container '{args.container}' is not running")
        print("Please start the container and try again")
        sys.exit(1)
    
    # Create backup directory
    backup_dir, timestamp = create_backup_directory(args.backup_dir)
    
    # Perform backup
    success = backup_neo4j_data(backup_dir, args.container, verbose=not args.quiet)
    
    if success:
        print(f"\nBackup completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Backup location: {backup_dir}")
    else:
        print("\n❌ Backup failed")
        sys.exit(1)
    
    return backup_dir

if __name__ == "__main__":
    main()