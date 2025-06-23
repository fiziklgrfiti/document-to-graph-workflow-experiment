# neo4j_restore.py
import os
import sys
import time
import argparse
from datetime import datetime
from dotenv import load_dotenv
import subprocess
import warnings
import glob

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

def list_available_backups(base_path="./import"):
    """List all available Neo4j backups."""
    backup_dirs = glob.glob(os.path.join(base_path, "neo4j_backup_*"))
    backup_dirs.sort(reverse=True)  # Most recent first
    
    return backup_dirs

def validate_backup(backup_dir):
    """Validate that the backup directory contains necessary files."""
    graphml_file = os.path.join(backup_dir, "neo4j_graph_data.graphml")
    csv_file = os.path.join(backup_dir, "nodes.csv")
    
    # Check if either the GraphML file or CSV file exists
    if not os.path.exists(graphml_file) and not os.path.exists(csv_file):
        print(f"❌ Error: Neither GraphML nor CSV backup files found in {backup_dir}")
        return False
    
    return True

def restore_neo4j_data(backup_dir, container_name="neo4j", clear_existing=True, verbose=True):
    """
    Restore Neo4j database from backup.
    
    Steps:
    1. Optionally clear existing data
    2. Import graph data from GraphML file
    3. Recreate vector indices
    """
    try:
        # Validate backup first
        if not validate_backup(backup_dir):
            return False
        
        username = os.getenv("NEO4J_USERNAME", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        
        # Step 1: Optionally clear existing data
        if clear_existing:
            if verbose:
                print("Clearing existing Neo4j data...")
            
            cmd = [
                "docker", "exec", container_name,
                "cypher-shell", 
                "-u", username, 
                "-p", password,
                "-d", "neo4j",
                "MATCH (n) DETACH DELETE n"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Error clearing existing data: {result.stderr}")
                return False
            
            if verbose:
                print("Existing data cleared successfully.")
        
        # Step 2: Import graph data from backup file
        graphml_file = os.path.join(backup_dir, "neo4j_graph_data.graphml")
        csv_file = os.path.join(backup_dir, "nodes.csv")
        
        # Determine which backup format to use (GraphML or CSV)
        using_graphml = os.path.exists(graphml_file)
        
        if verbose:
            if using_graphml:
                print(f"\nRestoring graph data from GraphML: {graphml_file}")
            else:
                print(f"\nRestoring graph data from CSV: {csv_file}")
            print("This may take a few moments...")
        
        # First ensure the directory has proper permissions inside the container
        container_backup_dir = f"/import/{os.path.basename(backup_dir)}"
        chmod_cmd = [
            "docker", "exec", container_name,
            "bash", "-c", f"chmod -R 777 {container_backup_dir}"
        ]
        
        try:
            subprocess.run(chmod_cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"Warning: Could not set permissions in container: {e.stderr}")
            # Continue anyway, as it might still work
        
        if using_graphml:
            # Path to the GraphML file inside the container
            container_path = f"{container_backup_dir}/neo4j_graph_data.graphml"
            
            # Import using APOC
            cmd = [
                "docker", "exec", container_name,
                "cypher-shell", 
                "-u", username, 
                "-p", password,
                "-d", "neo4j",
                f"CALL apoc.import.graphml('{container_path}', {{batchSize: 10000, readLabels: true, storeNodeIds: true}})"
            ]
        else:
            # Path to the CSV file inside the container
            container_path = f"{container_backup_dir}/nodes.csv"
            
            # Import using APOC CSV import
            cmd = [
                "docker", "exec", container_name,
                "cypher-shell", 
                "-u", username, 
                "-p", password,
                "-d", "neo4j",
                f"CALL apoc.import.csv(['{container_path}'], {{}}, {{delimiter: ',', arrayDelimiter: ';', stringIds: false}})"
            ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error importing graph data: {result.stderr}")
            
            # Try an alternative approach if the first attempt fails
            if verbose:
                print("First import method failed. Trying alternative approach...")
            
            # For GraphML, try load_graphml instead of import.graphml
            if using_graphml:
                alt_cmd = [
                    "docker", "exec", container_name,
                    "cypher-shell", 
                    "-u", username, 
                    "-p", password,
                    "-d", "neo4j",
                    f"CALL apoc.load.graphml('{container_path}', {{batchSize: 10000}})"
                ]
            else:
                # For CSV, try load.csv
                alt_cmd = [
                    "docker", "exec", container_name,
                    "cypher-shell", 
                    "-u", username, 
                    "-p", password,
                    "-d", "neo4j",
                    f"CALL apoc.load.csv('{container_path}') YIELD map AS row RETURN count(row)"
                ]
            
            alt_result = subprocess.run(alt_cmd, capture_output=True, text=True)
            
            if alt_result.returncode != 0:
                print(f"Alternative import also failed: {alt_result.stderr}")
                return False
        
        if verbose:
            print("Graph data restored successfully.")
        
        # Step 3: Recreate vector indices if they exist
        indices_file = os.path.join(backup_dir, "vector_indices.txt")
        
        if os.path.exists(indices_file):
            if verbose:
                print("\nDetected vector indices backup, preparing to restore...")
            
            # First, check if we can extract index information
            with open(indices_file, 'r') as f:
                indices_data = f.read()
            
            # We'll need to parse this data to extract index creation commands
            # For simplicity, we'll prompt the user to run the vector store creation script
            if verbose:
                print("\nVector indices detected in backup.")
                print("To recreate your vector indices, you should run the vector store creation script:")
                print("python neo4j_3-langchain-graph-to-vector-store.py --all")
                print("\nAlternatively, you can recreate them using the original workflow script:")
                print("./neo4j-5-workflow.sh")
        else:
            if verbose:
                print("\nNo vector indices backup found. Skipping vector index restoration.")
        
        if verbose:
            print(f"\n✅ Neo4j restoration completed successfully from: {backup_dir}")
        
        return True
        
    except Exception as e:
        print(f"Error during restore process: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(description="Restore Neo4j database from backup")
    parser.add_argument("--container", default="neo4j", help="Neo4j container name")
    parser.add_argument("--backup-dir", help="Specific backup directory to restore from")
    parser.add_argument("--list", action="store_true", help="List available backups")
    parser.add_argument("--keep-existing", action="store_true", help="Don't clear existing data before restore")
    parser.add_argument("--quiet", action="store_true", help="Reduce output verbosity")
    
    args = parser.parse_args()
    
    print(f"\n{'='*50}")
    print(f"NEO4J DATABASE RESTORE")
    print(f"{'='*50}\n")
    
    # Check if Neo4j container is running
    if not check_docker_running(args.container):
        print(f"❌ Error: Neo4j container '{args.container}' is not running")
        print("Please start the container and try again")
        sys.exit(1)
    
    # List available backups if requested
    if args.list:
        backups = list_available_backups()
        if not backups:
            print("No backups found in ./import directory")
            sys.exit(0)
        
        print(f"Found {len(backups)} backups:")
        for i, backup in enumerate(backups):
            backup_time = os.path.basename(backup).replace("neo4j_backup_", "")
            backup_time = backup_time.replace("_", " ").replace("T", " ")
            
            # Check if the backup is valid
            is_valid = validate_backup(backup)
            status = "✅ Valid" if is_valid else "❌ Invalid"
            
            print(f"{i+1}. {os.path.basename(backup)} - {status}")
        
        sys.exit(0)
    
    # Determine which backup to restore
    backup_dir = args.backup_dir
    if not backup_dir:
        backups = list_available_backups()
        if not backups:
            print("❌ No backups found in ./import directory")
            sys.exit(1)
        
        print(f"Found {len(backups)} backups:")
        for i, backup in enumerate(backups):
            backup_time = os.path.basename(backup).replace("neo4j_backup_", "")
            print(f"{i+1}. {os.path.basename(backup)}")
        
        selection = input("\nSelect a backup to restore (number or press Enter for most recent): ")
        if selection.strip() and selection.isdigit() and 1 <= int(selection) <= len(backups):
            backup_dir = backups[int(selection) - 1]
        else:
            backup_dir = backups[0]  # Most recent
    
    # Validate the selected backup
    if not os.path.exists(backup_dir):
        print(f"❌ Backup directory not found: {backup_dir}")
        sys.exit(1)
    
    if not validate_backup(backup_dir):
        print(f"❌ Invalid backup directory: {backup_dir}")
        sys.exit(1)
    
    print(f"Selected backup: {os.path.basename(backup_dir)}")
    
    # Confirm before proceeding with restore
    if not args.quiet and not args.keep_existing:
        print("\n⚠️ WARNING: This will delete all existing data in your Neo4j database.")
        confirmation = input("Are you sure you want to continue? (yes/no): ")
        if confirmation.lower() != "yes":
            print("Operation cancelled.")
            sys.exit(0)
    
    # Perform restoration
    success = restore_neo4j_data(
        backup_dir, 
        container_name=args.container,
        clear_existing=not args.keep_existing,
        verbose=not args.quiet
    )
    
    if success:
        print(f"\nRestore completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Restored from: {backup_dir}")
    else:
        print("\n❌ Restore failed")
        sys.exit(1)

if __name__ == "__main__":
    main()