# neo4j_connection.py
import os
from langchain_community.graphs import Neo4jGraph
from dotenv import load_dotenv

import warnings
warnings.filterwarnings("ignore")

# Load environment variables from .env file
load_dotenv()

# Connection parameters
url = "bolt://localhost:7687"
username = os.getenv("NEO4J_USERNAME") # Get username from .env file
password = os.getenv("NEO4J_PASSWORD")  # Get password from .env file

# Initialize Neo4j connection
graph = Neo4jGraph(
    url=url,
    username=username,
    password=password
)

# Test connection by running a simple query
result = graph.query("MATCH (n) RETURN count(n) as count")
print(f"Database contains {result[0]['count']} nodes.")