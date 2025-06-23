# neo4j_9-entity-duplicate-detection.py
import os
import argparse
from dotenv import load_dotenv
import warnings
from typing import List, Dict, Any, Optional, Tuple, Set
import time
import json
from pathlib import Path
import uuid

# LangChain imports
from langchain_community.graphs import Neo4jGraph
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

# Load environment variables from .env file
load_dotenv()
warnings.filterwarnings("ignore")

# Global verbose flag
VERBOSE = False

def initialize_neo4j_connection() -> Neo4jGraph:
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
        raise e

def initialize_llm(model_name: str = "llama3.1:latest", temperature: float = 0.1) -> Ollama:
    """Initialize and return the LLM."""
    # List of models to try in order of preference
    models_to_try = [
        model_name,        # Try the specified model first
        "gemma3:12b",      # Good general model
        "gemma3:4b",       # Smaller alternative
        "llama3.1:latest",  # Another alternative
        "deepseek-r1:8b"       # Fallback option
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

def get_graph_statistics(graph: Neo4jGraph) -> Dict[str, Any]:
    """Get basic statistics about the graph structure."""
    stats = {}
    
    # Get node count by label using a simpler, safer approach
    try:
        # Get all labels first
        label_results = []
        labels = graph.query("CALL db.labels() YIELD label RETURN label")
        
        for row in labels:
            label = row["label"]
            try:
                # For each label, get the count separately
                count_query = f"MATCH (n:{label}) RETURN count(n) AS count"
                count_result = graph.query(count_query)
                label_results.append({
                    "label": label, 
                    "count": count_result[0]["count"] if count_result else 0
                })
            except Exception as e:
                print(f"Warning: Error counting nodes with label {label}: {e}")
                # Still include the label but with count 0
                label_results.append({"label": label, "count": 0})
        
        stats["node_labels"] = label_results
        
        # Calculate total nodes
        total_nodes = sum(record["count"] for record in label_results)
        stats["total_nodes"] = total_nodes
        
    except Exception as e:
        print(f"❌ Error getting node statistics: {e}")
        stats["node_labels"] = []
        stats["total_nodes"] = 0
    
    # Get relationship count by type using a similar safe approach
    try:
        # Get all relationship types first
        rel_results = []
        rel_types = graph.query("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType")
        
        for row in rel_types:
            rel_type = row["relationshipType"]
            try:
                # For each type, get the count separately
                count_query = f"MATCH ()-[r:{rel_type}]->() RETURN count(r) AS count"
                count_result = graph.query(count_query)
                rel_results.append({
                    "relationship_type": rel_type, 
                    "count": count_result[0]["count"] if count_result else 0
                })
            except Exception as e:
                print(f"Warning: Error counting relationships of type {rel_type}: {e}")
                # Still include the type but with count 0
                rel_results.append({"relationship_type": rel_type, "count": 0})
        
        stats["relationship_types"] = rel_results
        
        # Calculate total relationships
        total_relationships = sum(record["count"] for record in rel_results)
        stats["total_relationships"] = total_relationships
        
    except Exception as e:
        print(f"❌ Error getting relationship statistics: {e}")
        stats["relationship_types"] = []
        stats["total_relationships"] = 0
    
    return stats

def get_all_entity_properties(graph: Neo4jGraph, label: str) -> Dict[str, Set[str]]:
    """Get all unique property keys and sample values for a specific entity type."""
    try:
        # Check if the label exists first to avoid warnings about non-existent labels
        check_query = """
        CALL db.labels() YIELD label
        WHERE label = $label
        RETURN count(*) > 0 AS exists
        """
        
        check_result = graph.query(check_query, params={"label": label})
        if not check_result or not check_result[0].get("exists", False):
            print(f"Label '{label}' not found in database, skipping property extraction.")
            return {}
        
        # Now proceed with property extraction since we know the label exists
        query = f"""
        MATCH (n:{label})
        WITH keys(n) AS keys, n
        UNWIND keys AS key
        RETURN DISTINCT key AS property_key, 
               collect(DISTINCT n[key])[0..5] AS sample_values,
               count(DISTINCT n) AS entity_count,
               count(DISTINCT n[key]) AS unique_values_count
        """
        
        property_data = graph.query(query)
        
        # Format the results into a more useful dictionary
        result = {}
        for item in property_data:
            prop_key = item["property_key"]
            sample_values = item["sample_values"]
            entity_count = item["entity_count"]
            unique_values_count = item["unique_values_count"]
            
            # Format sample values for display
            formatted_samples = []
            for val in sample_values:
                if isinstance(val, (list, dict)):
                    # Convert complex types to string for display
                    formatted_samples.append(str(val))
                else:
                    formatted_samples.append(val)
            
            result[prop_key] = {
                "sample_values": formatted_samples,
                "entity_count": entity_count,
                "unique_values_count": unique_values_count
            }
        
        return result
        
    except Exception as e:
        print(f"❌ Error getting properties for {label}: {e}")
        return {}

def identify_potential_duplicate_entity_types(graph: Neo4jGraph, llm: Ollama) -> List[Dict[str, Any]]:
    """
    Use LLM to analyze entity types (node labels) and identify potential duplicates.
    Returns a list of potential duplicate groups with reasoning.
    """
    # Get graph statistics
    graph_stats = get_graph_statistics(graph)
    node_labels = graph_stats.get("node_labels", [])
    
    # If no labels found, return empty list
    if not node_labels:
        print("No entity types found in the graph")
        return []
    
    # If only one label, no duplicates possible
    if len(node_labels) <= 1:
        print("Only one entity type found in the graph, no duplicates possible")
        return []
    
    print(f"Analyzing {len(node_labels)} entity types for potential duplicates...")
    
    # First apply rule-based prefilter
    rule_based_duplicates = prefilter_duplicate_entity_types(node_labels)
    
    if rule_based_duplicates:
        print(f"✓ Identified {len(rule_based_duplicates)} potential duplicate entity type groups using rule-based analysis")
    
    # Get property information for each entity type
    entity_type_details = {}
    for label_info in node_labels:
        label = label_info["label"]
        entity_type_details[label] = get_all_entity_properties(graph, label)
    
    # Create prompt for LLM to analyze entity types
    prompt_template = """
    You are a knowledge graph expert analyzing a Neo4j graph database for potential duplicate entity types (node labels).
    Your goal is to identify entity types that likely represent the same concept and could be merged.

    IMPORTANT: Entity types in Neo4j can be case-sensitive, so "Person" and "person" may represent the same concept
    but are treated as different labels. Pay special attention to case variations.

    GRAPH INFORMATION:
    Entity types and counts:
    {entity_types_info}

    ENTITY TYPE DETAILS:
    {entity_type_details}

    TASK:
    Analyze the entity types and identify potential duplicates based on:
    1. Similar naming (e.g., "Person" and "person", "Vehicle" and "vehicle")
    2. Similar property structures
    3. Semantic similarities in what they represent
    4. Case variations of the same word (these are very likely duplicates)
    5. Singular/plural variations (e.g., "Weapon" and "Weapons")

    Even with minimal property information, you should identify case-variant duplicates 
    (like "Person"/"person", "Vehicle"/"vehicle") as these are almost certainly representing 
    the same entities and should be merged.

    For each potential duplicate group, provide:
    1. The entity types that might be duplicates
    2. Reasoning for why they might be duplicates
    3. Recommendations for how to merge them (which type to keep, which properties to preserve)
    4. Potential risks or considerations for merging

    Format your response as a list of JSON objects, one for each potential duplicate group:
    [
      {{
        "duplicate_types": ["Type1", "Type2", ...],
        "reasoning": "Detailed explanation of why these are likely duplicates...",
        "merge_recommendation": {{
          "keep_type": "TypeX",
          "property_handling": "Explanation of how to handle property conflicts...",
          "relationship_handling": "How relationships should be preserved..."
        }},
        "risks": "Potential issues to consider before merging..."
      }},
      ...
    ]

    Verify that the list is valid JSON, fix any invalid JSON before you continue.

    If no potential duplicates are found, return an empty list: []
    """
    
    # Format entity types info for the prompt
    entity_types_info = "\n".join([f"- {item['label']}: {item['count']} nodes" for item in node_labels])
    
    # Format entity type details for the prompt
    details_parts = []
    for label, properties in entity_type_details.items():
        details_parts.append(f"Entity Type: {label}")
        if properties:
            for prop, info in properties.items():
                sample_str = ", ".join([str(s) for s in info["sample_values"]])
                details_parts.append(f"  - Property: {prop}")
                details_parts.append(f"    Sample values: {sample_str}")
                details_parts.append(f"    Present in {info['entity_count']} entities with {info['unique_values_count']} unique values")
        else:
            details_parts.append("  No properties found")
        details_parts.append("")  # Empty line for separation
    
    entity_type_details_str = "\n".join(details_parts)
    
    # Create the prompt
    prompt = PromptTemplate.from_template(prompt_template)
    
    # Run LLM analysis
    llm_duplicates = []
    try:
        # Create chain
        chain = prompt | llm | StrOutputParser()
        
        # Run the chain
        result_text = chain.invoke({
            "entity_types_info": entity_types_info,
            "entity_type_details": entity_type_details_str
        })
        
        # Parse the JSON result
        # First, find the JSON part in case the LLM added extra text
        json_start = result_text.find('[')
        json_end = result_text.rfind(']') + 1
        
        if json_start != -1 and json_end != -1:
            json_str = result_text[json_start:json_end]
            try:
                llm_duplicates = json.loads(json_str)
                print(f"✓ Identified {len(llm_duplicates)} potential duplicate entity type groups via LLM analysis")
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing LLM response as JSON: {e}")
                print("Raw LLM response:", result_text)
        else:
            print("❌ No valid JSON found in LLM response")
            print("Raw LLM response:", result_text)
        
    except Exception as e:
        print(f"❌ Error during entity type duplicate analysis: {e}")
    
    # If no duplicates found by LLM, fall back to rule-based results
    if not llm_duplicates and not rule_based_duplicates:
        # Check for case duplicates as a last resort
        duplicates_by_case = {}
        lowercase_labels = [label['label'].lower() for label in node_labels]
        
        for i, label in enumerate(node_labels):
            lowercase = label['label'].lower()
            if lowercase_labels.count(lowercase) > 1:
                if lowercase not in duplicates_by_case:
                    duplicates_by_case[lowercase] = []
                duplicates_by_case[lowercase].append(label['label'])
        
        # Generate suggestions
        for lowercase, variants in duplicates_by_case.items():
            if len(variants) > 1:
                rule_based_duplicates.append({
                    "duplicate_types": variants,
                    "reasoning": f"These labels appear to be case variations of the same concept: {variants}",
                    "merge_recommendation": {
                        "keep_type": variants[0],  # Default to first one
                        "property_handling": "Merge all properties",
                        "relationship_handling": "Preserve all relationships"
                    },
                    "risks": "Low risk - case variations typically represent the same concept"
                })
        
        if rule_based_duplicates:
            print(f"✓ Identified {len(rule_based_duplicates)} potential duplicate entity type groups using fallback analysis")
        
        return rule_based_duplicates
    
    # Combine results from both approaches, removing any duplicates
    all_duplicates = rule_based_duplicates.copy()
    
    # Helper function to check if a group is already covered
    def is_duplicate_group(group1, group2):
        set1 = set(group1.get("duplicate_types", []))
        set2 = set(group2.get("duplicate_types", []))
        # If there's significant overlap, consider them the same group
        return len(set1.intersection(set2)) > 0
    
    # Add LLM results if not already covered by rule-based results
    for llm_group in llm_duplicates:
        if not any(is_duplicate_group(llm_group, existing) for existing in all_duplicates):
            all_duplicates.append(llm_group)
    
    print(f"✓ Identified {len(all_duplicates)} total potential duplicate entity type groups")
    return all_duplicates

def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate the Levenshtein distance between two strings.
    This is a measure of string similarity - the minimum number of
    single-character edits required to change one string into the other.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def find_case_insensitive_duplicates(graph: Neo4jGraph) -> List[Dict[str, Any]]:
    """Find duplicate entity types based on case-insensitive comparison directly in Neo4j."""
    # Get all labels
    result = graph.query("CALL db.labels() YIELD label RETURN label")
    labels = [record["label"] for record in result]
    
    # Group by lowercase version
    groups = {}
    for label in labels:
        lowercase = label.lower()
        if lowercase in groups:
            groups[lowercase].append(label)
        else:
            groups[lowercase] = [label]
    
    # Filter to find duplicates
    duplicate_groups = []
    for lowercase, variants in groups.items():
        if len(variants) > 1:
            duplicate_groups.append({
                "duplicate_types": variants,
                "reasoning": f"These labels are identical except for case: {variants}",
                "merge_recommendation": {
                    "keep_type": variants[0],
                    "property_handling": "Merge all properties",
                    "relationship_handling": "Preserve all relationships"
                },
                "risks": "Low risk - case variations typically represent the same concept"
            })
    
    return duplicate_groups

def prefilter_duplicate_entity_types(node_labels: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Use simple rules to identify obvious duplicate candidates before LLM analysis."""
    labels = [item['label'] for item in node_labels]
    potential_duplicates = []
    
    # Check for case variations (e.g., "Person" vs "person")
    label_map = {}
    for label in labels:
        lowercase = label.lower()
        if lowercase in label_map:
            label_map[lowercase].append(label)
        else:
            label_map[lowercase] = [label]
    
    # Add all case variation groups
    for lowercase, variants in label_map.items():
        if len(variants) > 1:
            potential_duplicates.append({
                "duplicate_types": variants,
                "reasoning": f"Case variation of the same term: {variants}",
                "merge_recommendation": {
                    # Recommend keeping the version that appears most often in the data
                    "keep_type": max(variants, key=lambda x: next((item['count'] for item in node_labels if item['label'] == x), 0)),
                    "property_handling": "Merge all properties, keeping those from the most populous type if conflicts arise",
                    "relationship_handling": "Preserve all relationships from all entity types"
                },
                "risks": "Low risk for case variations as they almost certainly represent the same concept"
            })
    
    # Rule for singular/plural variations
    singular_plural_pairs = []
    for label1 in labels:
        for label2 in labels:
            if label1 != label2:
                # Check if one is the plural of the other
                if label1.lower() + 's' == label2.lower() or label2.lower() + 's' == label1.lower():
                    singular_plural_pairs.append([label1, label2])
    
    # Add all singular/plural groups
    for pair in singular_plural_pairs:
        potential_duplicates.append({
            "duplicate_types": pair,
            "reasoning": f"Singular/plural variation: {pair}",
            "merge_recommendation": {
                # Usually prefer the singular form
                "keep_type": min(pair, key=len),
                "property_handling": "Merge all properties, preferring those from the singular form if conflicts arise",
                "relationship_handling": "Preserve all relationships from both entity types"
            },
            "risks": "Low risk for singular/plural variations as they likely represent the same concept"
        })
    
    return potential_duplicates

def identify_potential_duplicate_entities(graph: Neo4jGraph, llm: Ollama, entity_type: str = None, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Use LLM to analyze entities of a specific type and identify potential duplicates.
    If entity_type is None, all entity types will be analyzed up to the limit per type.
    """
    if entity_type:
        # Analyze specific entity type
        entity_types = [entity_type]
    else:
        # Get all entity types from the graph
        try:
            result = graph.query("CALL db.labels() YIELD label RETURN label")
            entity_types = [record["label"] for record in result]
        except Exception as e:
            print(f"❌ Error getting entity types: {e}")
            return []
    
    all_duplicate_groups = []
    
    for current_type in entity_types:
        print(f"\nAnalyzing entities of type '{current_type}' for potential duplicates...")
        
        # Get entities of the current type
        try:
            query = f"""
            MATCH (n:{current_type})
            RETURN n.id as id, n.name as name, properties(n) as properties
            LIMIT {limit}
            """
            
            entities = graph.query(query)
            
            if not entities:
                print(f"No entities found of type '{current_type}'")
                continue
                
            print(f"Analyzing {len(entities)} entities of type '{current_type}'...")
            
            # Create prompt for LLM to analyze entities
            prompt_template = """
            You are a knowledge graph expert analyzing entities from a Neo4j graph database to identify potential duplicates.
            Your goal is to identify entities that likely represent the same real-world concept and could be merged.

            ENTITY TYPE: {entity_type}

            ENTITIES TO ANALYZE:
            {entities_info}

            TASK:
            Analyze the entities and identify potential duplicates based on:
            1. Similar or matching names (accounting for variations, misspellings, abbreviations)
            2. Similar property values
            3. Semantic similarities in what they represent
            4. Any other indicators that suggest they represent the same real-world entity

            For each potential duplicate group, provide:
            1. The entity IDs that might be duplicates
            2. The entity names
            3. Reasoning for why they might be duplicates
            4. Recommendations for how to merge them (which entity to keep, which properties to preserve)
            5. Confidence level (high, medium, low)

            Format your response as a list of JSON objects, one for each potential duplicate group:
            [
              {{
                "duplicate_ids": ["id1", "id2", ...],
                "duplicate_names": ["name1", "name2", ...],
                "reasoning": "Detailed explanation of why these are likely duplicates...",
                "merge_recommendation": {{
                  "keep_id": "id_to_keep",
                  "property_handling": "Explanation of how to handle property conflicts..."
                }},
                "confidence": "high/medium/low"
              }},
              ...
            ]

            If no potential duplicates are found, return an empty list: []
            """
            
            # Format entities info for the prompt
            entities_info_parts = []
            
            for i, entity in enumerate(entities):
                entity_id = entity.get("id", f"unknown_{i}")
                entity_name = entity.get("name", "Unnamed")
                properties = entity.get("properties", {})
                
                # Format properties, excluding id and name which are already displayed
                prop_parts = []
                for key, value in properties.items():
                    if key not in ["id", "name"]:
                        # Handle complex types like lists or dictionaries
                        if isinstance(value, (list, dict)):
                            value_str = str(value)
                        else:
                            value_str = str(value)
                        
                        # Truncate very long values
                        if len(value_str) > 100:
                            value_str = value_str[:97] + "..."
                            
                        prop_parts.append(f"{key}: {value_str}")
                
                props_str = ", ".join(prop_parts)
                
                # Add entity info to the list
                entities_info_parts.append(f"Entity ID: {entity_id}")
                entities_info_parts.append(f"Name: {entity_name}")
                entities_info_parts.append(f"Properties: {props_str}")
                entities_info_parts.append("")  # Empty line for separation
            
            entities_info_str = "\n".join(entities_info_parts)
            
            # Create the prompt
            prompt = PromptTemplate.from_template(prompt_template)
            
            # Run LLM analysis
            try:
                # Create chain
                chain = prompt | llm | StrOutputParser()
                
                # Run the chain
                result_text = chain.invoke({
                    "entity_type": current_type,
                    "entities_info": entities_info_str
                })
                
                # Parse the JSON result
                # First, find the JSON part in case the LLM added extra text
                json_start = result_text.find('[')
                json_end = result_text.rfind(']') + 1
                
                if json_start != -1 and json_end != -1:
                    json_str = result_text[json_start:json_end]
                    try:
                        duplicate_groups = json.loads(json_str)
                        
                        # Add entity type to each group
                        for group in duplicate_groups:
                            group["entity_type"] = current_type
                            
                        print(f"✓ Identified {len(duplicate_groups)} potential duplicate groups for '{current_type}'")
                        all_duplicate_groups.extend(duplicate_groups)
                        
                    except json.JSONDecodeError as e:
                        print(f"❌ Error parsing LLM response as JSON for '{current_type}': {e}")
                        print("Raw LLM response:", result_text[:500] + "..." if len(result_text) > 500 else result_text)
                else:
                    print(f"❌ No valid JSON found in LLM response for '{current_type}'")
                    print("Raw LLM response:", result_text[:500] + "..." if len(result_text) > 500 else result_text)
                
            except Exception as e:
                print(f"❌ Error during entity duplicate analysis for '{current_type}': {e}")
            
        except Exception as e:
            print(f"❌ Error getting entities of type '{current_type}': {e}")
    
    print(f"\nTotal potential duplicate groups identified: {len(all_duplicate_groups)}")
    return all_duplicate_groups

def create_resolution_plan(graph: Neo4jGraph, llm: Ollama, duplicate_groups: List[Dict[str, Any]], duplicate_type: str = "entity") -> Dict[str, Any]:
    """
    Use LLM to create a detailed resolution plan for the identified duplicates.
    duplicate_type can be "entity" or "entity_type" to specify what kind of duplicates we're resolving.
    """
    if not duplicate_groups:
        print("No duplicate groups to resolve")
        return {"groups": [], "resolution_plan": []}
    
    print(f"Creating resolution plan for {len(duplicate_groups)} {duplicate_type} duplicate groups...")
    
    # Fix duplicate groups first - if the same pairs appear multiple times, deduplicate them
    unique_groups = []
    seen_pairs = set()
    
    print(f"Original duplicate groups count: {len(duplicate_groups)}")
    
    for group in duplicate_groups:
        # For entity_type, check duplicate_types
        if duplicate_type == "entity_type":
            items = tuple(sorted(group.get("duplicate_types", [])))
            if items and items not in seen_pairs and len(items) > 1:  # Ensure there are at least 2 items
                seen_pairs.add(items)
                unique_groups.append(group)
        # For entities, check duplicate_ids
        else:
            items = tuple(sorted(group.get("duplicate_ids", [])))
            if items and items not in seen_pairs and len(items) > 1:  # Ensure there are at least 2 items
                seen_pairs.add(items)
                unique_groups.append(group)
    
    # Use the deduplicated groups for the rest of the function
    duplicate_groups = unique_groups
    print(f"Deduplicated groups count: {len(duplicate_groups)}")
    
    
    # Get some graph statistics for context
    graph_stats = get_graph_statistics(graph)
    
    # For entity type resolution, we need to understand relationships between types
    type_relationship_info = ""
    if duplicate_type == "entity_type":
        try:
            # Get relationship patterns between entity types
            type_rel_query = """
            MATCH (a)-[r]->(b)
            WITH labels(a)[0] AS a_label, type(r) AS rel_type, labels(b)[0] AS b_label, count(*) AS count
            RETURN a_label, rel_type, b_label, count
            ORDER BY count DESC
            LIMIT 50
            """
            
            type_rel_results = graph.query(type_rel_query)
            
            # Format relationship patterns
            if type_rel_results:
                type_rel_parts = ["Relationship patterns between entity types:"]
                for item in type_rel_results:
                    type_rel_parts.append(f"- {item['a_label']} -[{item['rel_type']}]-> {item['b_label']} ({item['count']} instances)")
                type_relationship_info = "\n".join(type_rel_parts)
            
        except Exception as e:
            print(f"❌ Error getting type relationship information: {e}")
            type_relationship_info = "Error retrieving relationship pattern information."
    
    # Create prompt for LLM to create resolution plan
    prompt_template = """
    You are a knowledge graph expert creating a detailed plan to resolve {duplicate_type} duplicates in a Neo4j graph database.
    Your goal is to provide precise, step-by-step Cypher queries and instructions to safely merge duplicates while preserving data integrity.

    GRAPH INFORMATION:
    Total nodes: {total_nodes}
    Total relationships: {total_relationships}
    Node labels: {node_labels}
    Relationship types: {relationship_types}
    
    {type_relationship_info}

    IDENTIFIED DUPLICATE GROUPS:
    {duplicate_groups}

    TASK:
    For each duplicate group, create a detailed resolution plan that includes:
    1. A summary of what will be merged
    2. Pre-merge validation queries to confirm the duplicates are safe to merge
    3. Exact Cypher queries to perform the merge operations
    4. Post-merge validation queries to confirm success

    Your plan should prioritize data safety and integrity. Each step should be carefully designed to:
    - Preserve all unique property values where possible
    - Maintain all existing relationships
    - Be idempotent where possible (can be run multiple times without causing issues)
    - Include validations before destructive operations

    Format your response as a JSON object with the following structure:
    {{
      "groups": [
        {{
          "group_id": "unique_identifier_for_group",
          "group_summary": "Human-readable summary of what will be merged",
          "items": ["list", "of", "entities", "or", "types", "to", "merge"],
          "merge_target": "id_or_type_to_keep",
          "impact_assessment": "Description of what data will be affected"
        }},
        ...
      ],
      "resolution_plan": [
        {{
          "group_id": "corresponding_to_group_above",
          "pre_merge_validation": [
            {{
              "query": "CYPHER QUERY",
              "description": "What this query checks for",
              "success_criteria": "How to interpret results"
            }},
            ...
          ],
          "merge_operations": [
            {{
              "query": "CYPHER QUERY",
              "description": "What this operation does",
              "requires_confirmation": true/false
            }},
            ...
          ],
          "post_merge_validation": [
            {{
              "query": "CYPHER QUERY",
              "description": "What this query verifies",
              "success_criteria": "How to interpret results"
            }},
            ...
          ]
        }},
        ...
      ]
    }}
    
    # NEW PROMPT INSTRUCTIONS START
    CRITICAL INSTRUCTION:
    For entity type merges, ensure that:
    1. The queries for each group match EXACTLY the entity types mentioned in that group
    2. Do not mix queries for different entity types - each group should only have operations for the specific types listed in the group
    3. For each group, verify that pre-merge, merge, and post-merge operations all target the SAME entity types
    4. NEVER use generic operations - always use the specific entity type names in each query
    5. Assign a uuid-style unique ID to each group_id
    # NEW PROMPT INSTRUCTIONS END
    """
    
    # Format graph stats for the prompt
    node_labels_str = ", ".join([f"{item['label']} ({item['count']})" for item in graph_stats.get("node_labels", [])])
    rel_types_str = ", ".join([f"{item['relationship_type']} ({item['count']})" for item in graph_stats.get("relationship_types", [])])
    
    # Format duplicate groups for the prompt
    duplicate_groups_str = json.dumps(duplicate_groups, indent=2)
    
    # Create the prompt
    prompt = PromptTemplate.from_template(prompt_template)
    
    # Run LLM analysis
    try:
        # Create chain
        chain = prompt | llm | StrOutputParser()
        
        # Run the chain
        result_text = chain.invoke({
            "duplicate_type": duplicate_type,
            "total_nodes": graph_stats.get("total_nodes", 0),
            "total_relationships": graph_stats.get("total_relationships", 0),
            "node_labels": node_labels_str,
            "relationship_types": rel_types_str,
            "type_relationship_info": type_relationship_info,
            "duplicate_groups": duplicate_groups_str
        })
        
        # Parse the JSON result
        # First, find the JSON part in case the LLM added extra text
        json_start = result_text.find('{')
        json_end = result_text.rfind('}') + 1
        
        if json_start != -1 and json_end != -1:
            json_str = result_text[json_start:json_end]
            try:
                resolution_plan = json.loads(json_str)
                # Check that each group has matching operations
                for group in resolution_plan.get("groups", []):
                    # Ensure each group has a unique UUID-style group_id if not already present
                    if not group.get("group_id") or len(group.get("group_id", "")) < 8:
                        group["group_id"] = str(uuid.uuid4())
                
                # Validate that each resolution plan matches its corresponding group
                for plan in resolution_plan.get("resolution_plan", []):
                    group_id = plan.get("group_id")
                    group = next((g for g in resolution_plan.get("groups", []) if g.get("group_id") == group_id), None)
                    
                    if group:
                        items = group.get("items", [])
                        if not items:
                            continue
                            
                        # Check pre-merge validation queries
                        for validation in plan.get("pre_merge_validation", []):
                            query = validation.get("query", "").upper()
                            # Make sure at least one of the items is referenced in the query
                            if not any(item.upper() in query for item in items):
                                print(f"WARNING: Query doesn't reference expected entities: {validation.get('query')}")
                                print(f"Expected entities: {items}")
                                # Try to fix the query by replacing generic references
                
                print(f"✓ Created resolution plan with {len(resolution_plan.get('groups', []))} groups")
                print(f"DEBUG: Resolution plan has {len(resolution_plan.get('groups', []))} groups and {len(resolution_plan.get('resolution_plan', []))} resolution steps")
                print(f"DEBUG: Resolution plan structure summary:")
                print(f"  - Groups: {len(resolution_plan.get('groups', []))}")
                print(f"  - Resolution steps: {len(resolution_plan.get('resolution_plan', []))}")
                print(f"  - Group IDs: {[g.get('group_id', 'missing') for g in resolution_plan.get('groups', [])]}")
                print(f"  - Resolution plan group IDs: {[p.get('group_id', 'missing') for p in resolution_plan.get('resolution_plan', [])]}")
                return resolution_plan
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing LLM response as JSON: {e}")
                print("Raw LLM response:", result_text[:500] + "..." if len(result_text) > 500 else result_text)
                return {"groups": [], "resolution_plan": []}
        else:
            print("❌ No valid JSON found in LLM response")
            print("Raw LLM response:", result_text[:500] + "..." if len(result_text) > 500 else result_text)
            return {"groups": [], "resolution_plan": []}
        
    except Exception as e:
        print(f"❌ Error creating resolution plan: {e}")
        return {"groups": [], "resolution_plan": []}

def ensure_items_in_resolution_plan(resolution_plan, duplicate_groups, duplicate_type):
    """
    Ensure that each group in the resolution plan has its 'items' field populated.
    This is especially important for entity type duplicates.
    """
    if not resolution_plan:
        return resolution_plan
    
    if not isinstance(resolution_plan, dict):
        print("Warning: Resolution plan is not properly formatted (expected dictionary)")
        return resolution_plan
    
    groups = resolution_plan.get("groups", [])
    if not isinstance(groups, list):
        print("Warning: Resolution plan groups is not properly formatted (expected list)")
        return resolution_plan
        
    for group in resolution_plan.get("groups", []):
        # If items is missing or empty but duplicate_types exists, use that
        if not group.get("items"):
            # For entity types, try to find matching duplicate group
            if duplicate_type == "entity_type":
                # First try to match by duplicate_types
                for dup_group in duplicate_groups:
                    if set(dup_group.get("duplicate_types", [])) == set(group.get("duplicate_types", [])):
                        group["items"] = dup_group.get("duplicate_types", [])
                        break
                
                # If still no items, use any available fields
                if not group.get("items"):
                    for field in ["duplicate_types", "types", "entities"]:
                        if group.get(field):
                            group["items"] = group.get(field)
                            break
                            
            # For entities, use duplicate_ids
            elif duplicate_type == "entity":
                for dup_group in duplicate_groups:
                    if set(dup_group.get("duplicate_ids", [])) == set(group.get("duplicate_ids", [])):
                        group["items"] = dup_group.get("duplicate_ids", [])
                        break
    
    return resolution_plan

def format_resolution_plan_for_display(resolution_plan: Dict[str, Any]) -> str:
    """Format the resolution plan in a human-readable way for display and verification."""
    if not resolution_plan or not resolution_plan.get("groups"):
        return "No resolution plan available."
    
    display_parts = []
    
    # Header
    display_parts.append("\n" + "="*80)
    display_parts.append("DUPLICATE RESOLUTION PLAN")
    display_parts.append("="*80 + "\n")
    
    # Summary of groups
    display_parts.append(f"Total groups to resolve: {len(resolution_plan.get('groups', []))}\n")
    
    # Detail for each group
    for i, group in enumerate(resolution_plan.get("groups", [])):
        display_parts.append(f"GROUP {i+1}: {group.get('group_summary', 'Unknown')}")
        display_parts.append(f"Items to merge: {', '.join(group.get('items', []))}")
        display_parts.append(f"Target to keep: {group.get('merge_target', 'Unknown')}")
        display_parts.append(f"Impact: {group.get('impact_assessment', 'Unknown')}")
        display_parts.append("")  # Empty line
    
    # Detailed resolution plan
    display_parts.append("\n" + "="*80)
    display_parts.append("DETAILED RESOLUTION STEPS")
    display_parts.append("="*80 + "\n")
    
    for i, plan in enumerate(resolution_plan.get("resolution_plan", [])):
        # Find corresponding group
        group_id = plan.get("group_id")
        group = next((g for g in resolution_plan.get("groups", []) if g.get("group_id") == group_id), None)
        
        if group:
            display_parts.append(f"RESOLUTION PLAN FOR GROUP {i+1}: {group.get('group_summary', 'Unknown')}")
        else:
            display_parts.append(f"RESOLUTION PLAN {i+1}")
        display_parts.append("-" * 80)
        
        # Pre-merge validation
        display_parts.append("\nPRE-MERGE VALIDATION:")
        for j, validation in enumerate(plan.get("pre_merge_validation", [])):
            display_parts.append(f"Step {j+1}: {validation.get('description', 'Unknown check')}")
            display_parts.append(f"Query: {validation.get('query', 'No query')}")
            display_parts.append(f"Success criteria: {validation.get('success_criteria', 'Unknown')}")
            display_parts.append("")  # Empty line
        
        # Merge operations
        display_parts.append("\nMERGE OPERATIONS:")
        for j, operation in enumerate(plan.get("merge_operations", [])):
            confirmation = "⚠️ REQUIRES CONFIRMATION" if operation.get("requires_confirmation", True) else "Automatic"
            display_parts.append(f"Step {j+1}: {operation.get('description', 'Unknown operation')} ({confirmation})")
            display_parts.append(f"Query: {operation.get('query', 'No query')}")
            display_parts.append("")  # Empty line
        
        # Post-merge validation
        display_parts.append("\nPOST-MERGE VALIDATION:")
        for j, validation in enumerate(plan.get("post_merge_validation", [])):
            display_parts.append(f"Step {j+1}: {validation.get('description', 'Unknown check')}")
            display_parts.append(f"Query: {validation.get('query', 'No query')}")
            display_parts.append(f"Success criteria: {validation.get('success_criteria', 'Unknown')}")
            display_parts.append("")  # Empty line
        
        display_parts.append("="*80)  # Separator between plans
    
    return "\n".join(display_parts)

def save_resolution_plan(resolution_plan: Dict[str, Any], output_dir: str = "resolution_plans") -> str:
    """Save the resolution plan to a file for future reference."""
    # Sanitize output_dir to prevent directory traversal
    safe_dir = os.path.basename(output_dir)
    output_dir = safe_dir if safe_dir else "resolution_plans"

    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate a filename with timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"resolution_plan_{timestamp}.json"
    output_path = os.path.join(output_dir, filename)
    
    # Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(resolution_plan, f, indent=2)
    
    print(f"✓ Saved resolution plan to {output_path}")
    
    # Also save a human-readable version
    readable_filename = f"resolution_plan_{timestamp}.txt"
    readable_path = os.path.join(output_dir, readable_filename)
    
    with open(readable_path, 'w', encoding='utf-8') as f:
        f.write(format_resolution_plan_for_display(resolution_plan))
    
    print(f"✓ Saved human-readable resolution plan to {readable_path}")
    
    return output_path

def backup_neo4j_database(container_name: str = "neo4j"):
    """Create a backup of the Neo4j database before making changes."""
    try:
        # Check if backup script exists
        backup_script = "./neo4j_backup.py"
        if not os.path.exists(backup_script):
            print("❌ Backup script not found. Manual backup recommended before proceeding.")
            return False
        
        print("Creating Neo4j database backup...")
        
        # Execute the backup script
        import subprocess
        result = subprocess.run(["python", backup_script, "--container", container_name], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Database backup completed successfully")
            return True
        else:
            print(f"❌ Backup failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return False

def execute_cypher_query(graph: Neo4jGraph, query: str, params: Dict[str, Any] = None) -> Tuple[List[Dict[str, Any]], bool]:
    """Execute a Cypher query and return the results and success status."""
    try:
        if params is None:
            params = {}
        
        result = graph.query(query, params=params)
        return result, True
    except Exception as e:
        print(f"❌ Error executing query: {e}")
        print(f"Query: {query}")
        if params:
            print(f"Parameters: {params}")
        return [], False

def execute_resolution_plan(graph: Neo4jGraph, resolution_plan: Dict[str, Any], group_idx: int = None) -> bool:
    """
    Execute a resolution plan for duplicate entities or types.
    If group_idx is specified, only that group will be resolved. Otherwise, all groups will be processed.
    """
    try:
        if not resolution_plan or not resolution_plan.get("resolution_plan"):
            print("No resolution plan to execute")
            return False
        
        # If a specific group index is provided, only execute that group's plan
        if group_idx is not None:
            if group_idx < 0 or group_idx >= len(resolution_plan.get("groups", [])):
                print(f"❌ Invalid group index: {group_idx}. Valid range: 0-{len(resolution_plan.get('groups', [])) - 1}")
                return False
            
            # Find the corresponding resolution plan for this group
            group_id = resolution_plan["groups"][group_idx]["group_id"]
            plan_to_execute = [p for p in resolution_plan["resolution_plan"] if p.get("group_id") == group_id]
            
            if not plan_to_execute:
                print(f"❌ No resolution plan found for group {group_idx}")
                return False
                
            plans = plan_to_execute
            groups = [resolution_plan["groups"][group_idx]]
        else:
            # Execute all plans in order
            plans = resolution_plan.get("resolution_plan", [])
            groups = resolution_plan.get("groups", [])
        
        print(f"\nExecuting resolution plan for {len(groups)} groups...")
        
        execution_results = {
            "total_groups": len(groups),
            "successful_groups": 0,
            "failed_groups": 0,
            "skipped_groups": 0,
            "group_results": []
        }

        group_lookup = {g.get("group_id"): g for g in groups}
        
        for i, plan in enumerate(plans):
            group_id = plan.get("group_id")
            group = group_lookup.get(group_id)
            if not group:
                print(f"Warning: No matching group found for plan with group_id {group_id}")
                continue
            print(f"\n{'='*80}")
            print(f"EXECUTING PLAN FOR GROUP {i+1}: {group.get('group_summary', 'Unknown')}")
            print(f"{'='*80}\n")
            
            group_result = {
                "group_id": group.get("group_id"),
                "summary": group.get("group_summary"),
                "status": "pending",
                "details": [],
                "pre_validation_results": [],
                "operation_results": [],
                "post_validation_results": []
            }
            
            # Run pre-merge validation
            print("Running pre-merge validation...")
            validation_passed = True
            
            for j, validation in enumerate(plan.get("pre_merge_validation", [])):
                print(f"\nPre-merge validation {j+1}: {validation.get('description', 'Unknown check')}")
                print(f"Query: {validation.get('query', 'No query')}")
                
                query_results, success = execute_cypher_query(graph, validation.get("query", ""))

                group_result["pre_validation_results"].append({
                    "step": j+1,
                    "description": validation.get("description", "Unknown check"),
                    "query": validation.get("query", "No query"),
                    "success": success,
                    "result_count": len(query_results) if query_results else 0,
                    "sample_results": query_results[:5] if query_results else []
                })
                                
                
                if not success:
                    print(f"❌ Validation query failed. Skipping this group.")
                    validation_passed = False
                    
                    group_result["status"] = "pre_validation_failed"
                    group_result["details"].append(f"Pre-validation step {j+1} failed: Query execution error")
                    
                    
                    break
                
                # Display results
                print("Results:")
                if not query_results:
                    print("  No results returned")
                else:
                    for k, result in enumerate(query_results[:5]):  # Show at most 5 results
                        print(f"  Result {k+1}: {result}")
                    
                    if len(query_results) > 5:
                        print(f"  ... and {len(query_results) - 5} more results")
                
                # Ask for confirmation to proceed
                success_criteria = validation.get("success_criteria", "")
                if success_criteria:
                    print(f"Success criteria: {success_criteria}")
                
                proceed = input("\nDoes this validation pass? (y/n): ").lower() == 'y'
                
                group_result["pre_validation_results"][-1]["user_approved"] = proceed
                
                
                if not proceed:
                    print("❌ Validation did not pass. Skipping this group.")
                    validation_passed = False
                    
                    group_result["status"] = "pre_validation_rejected"
                    group_result["details"].append(f"Pre-validation step {j+1} rejected by user")
                    
                    
                    break
            
            if not validation_passed:
                execution_results["skipped_groups"] += 1
                execution_results["group_results"].append(group_result)
                
                
                continue
            
            # Run merge operations
            print("\nRunning merge operations...")
            merge_successful = True
            
            for j, operation in enumerate(plan.get("merge_operations", [])):
                print(f"\nMerge operation {j+1}: {operation.get('description', 'Unknown operation')}")
                print(f"Query: {operation.get('query', 'No query')}")
                
                operation_result = {
                    "step": j+1,
                    "description": operation.get("description", "Unknown operation"),
                    "query": operation.get("query", "No query"),
                    "requires_confirmation": operation.get("requires_confirmation", True),
                    "executed": False,
                    "success": False,
                    "records_affected": 0
                }
                
                
                # Ask for confirmation if required
                if operation.get("requires_confirmation", True):
                    print("\n⚠️ WARNING: This operation may modify or delete data")
                    proceed = input("Do you want to proceed with this operation? (y/n): ").lower() == 'y'
                    
                    operation_result["user_approved"] = proceed
                    
                    
                    if not proceed:
                        print("Operation skipped by user.")
                        merge_successful = False
                        
                        group_result["status"] = "operation_rejected"
                        group_result["details"].append(f"Operation step {j+1} rejected by user")
                        operation_result["user_skipped"] = True
                        group_result["operation_results"].append(operation_result)
                        
                        
                        break
                
                query_results, success = execute_cypher_query(graph, operation.get("query", ""))
                
                operation_result["executed"] = True
                operation_result["success"] = success
                operation_result["records_affected"] = len(query_results) if query_results else 0
                group_result["operation_results"].append(operation_result)
                
                
                if not success:
                    print(f"❌ Operation failed. Skipping remaining operations for this group.")
                    merge_successful = False
                    
                    group_result["status"] = "operation_failed"
                    group_result["details"].append(f"Operation step {j+1} failed: Query execution error")
                    
                    
                    break
                
                # Display results summary
                print("Operation completed:")
                if not query_results:
                    print("  No results returned")
                else:
                    print(f"  {len(query_results)} records affected")
            
            if not merge_successful:
                execution_results["failed_groups"] += 1
                execution_results["group_results"].append(group_result)
                
                
                continue
            
            # Run post-merge validation
            print("\nRunning post-merge validation...")
            post_validation_passed = True
            
            for j, validation in enumerate(plan.get("post_merge_validation", [])):
                print(f"\nPost-merge validation {j+1}: {validation.get('description', 'Unknown check')}")
                print(f"Query: {validation.get('query', 'No query')}")
                
                query_results, success = execute_cypher_query(graph, validation.get("query", ""))

                group_result["post_validation_results"].append({
                    "step": j+1,
                    "description": validation.get("description", "Unknown check"),
                    "query": validation.get("query", "No query"),
                    "success": success,
                    "result_count": len(query_results) if query_results else 0,
                    "sample_results": query_results[:5] if query_results else []
                })
                                
                
                if not success:
                    print(f"❌ Validation query failed. Group might not be fully resolved.")
                    post_validation_passed = False
                    
                    group_result["status"] = "post_validation_failed"
                    group_result["details"].append(f"Post-validation step {j+1} failed: Query execution error")
                    
                    
                    break
                
                # Display results
                print("Results:")
                if not query_results:
                    print("  No results returned")
                else:
                    for k, result in enumerate(query_results[:5]):  # Show at most 5 results
                        print(f"  Result {k+1}: {result}")
                    
                    if len(query_results) > 5:
                        print(f"  ... and {len(query_results) - 5} more results")
                
                # Ask for confirmation to proceed
                success_criteria = validation.get("success_criteria", "")
                if success_criteria:
                    print(f"Success criteria: {success_criteria}")
                
                validation_passes = input("\nDoes this validation pass? (y/n): ").lower() == 'y'
                
                group_result["post_validation_results"][-1]["user_approved"] = validation_passes
                
                
                if not validation_passes:
                    print("❌ Post-merge validation did not pass. Group might not be fully resolved.")
                    post_validation_passed = False
                    
                    group_result["status"] = "post_validation_rejected"
                    group_result["details"].append(f"Post-validation step {j+1} rejected by user")
                    
                    
                    break
            
            if validation_passed and merge_successful and post_validation_passed:
                print(f"\n✓ Successfully resolved group: {group.get('group_summary', 'Unknown')}")
                group_result["status"] = "success"
                execution_results["successful_groups"] += 1
            else:
                if post_validation_passed:
                    # If we get here with failed validations, it's a partial success
                    print(f"\n⚠️ Group partially resolved with validation issues: {group.get('group_summary', 'Unknown')}")
                    group_result["status"] = "partial_success"
                    execution_results["failed_groups"] += 1
                else:
                    # Already counted as failed above
                    print(f"\n⚠️ Group failed to resolve: {group.get('group_summary', 'Unknown')}")
            
            execution_results["group_results"].append(group_result)
        
        print("\n" + "="*80)
        print("RESOLUTION PLAN EXECUTION RESULTS")
        print("="*80)
        print(f"Total groups: {execution_results['total_groups']}")
        print(f"Successfully resolved: {execution_results['successful_groups']}")
        print(f"Failed: {execution_results['failed_groups']}")
        print(f"Skipped: {execution_results['skipped_groups']}")
        
        # Save execution report to file
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = f"resolution_plans/execution_report_{timestamp}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(execution_results, f, indent=2)
            print(f"✓ Saved execution report to {report_file}")
        except Exception as e:
            print(f"❌ Failed to save execution report: {e}")
        
        print("="*80)
        print("\nResolution plan execution completed")
        return execution_results["failed_groups"] <= 0
    except Exception as e:
        print(f"❌ Error executing resolution plan: {e}")
        import traceback
        traceback.print_exc()
        return False

def interactive_duplicate_resolution(graph: Neo4jGraph, llm: Ollama, container_name: str = "neo4j"):
    """Interactive workflow for identifying and resolving duplicates."""
    print("\n" + "="*80)
    print("INTERACTIVE DUPLICATE RESOLUTION WORKFLOW")
    print("="*80 + "\n")
    
    # Step 1: Choose what to analyze
    print("Step 1: Choose what to analyze")
    print("1. Entity types (labels)")
    print("2. Entities of a specific type")
    print("3. All entities (analyze each type)")
    
    choice = input("\nEnter your choice (1-3): ")
    
    duplicate_groups = []
    analysis_type = ""
    entity_type = None
    
    if choice == "1":
        # Analyze entity types
        print("\nAnalyzing entity types for duplicates...")
        duplicate_groups = identify_potential_duplicate_entity_types(graph, llm)
        analysis_type = "entity_type"
    elif choice == "2":
        # Get available entity types
        try:
            result = graph.query("CALL db.labels() YIELD label RETURN label")
            available_types = [record["label"] for record in result]
            
            print("\nAvailable entity types:")
            for i, label in enumerate(available_types):
                print(f"{i+1}. {label}")
            
            type_choice = int(input("\nEnter the number of the entity type to analyze: "))
            
            if 1 <= type_choice <= len(available_types):
                entity_type = available_types[type_choice - 1]
                print(f"\nAnalyzing entities of type '{entity_type}' for duplicates...")
                duplicate_groups = identify_potential_duplicate_entities(graph, llm, entity_type)
                analysis_type = "entity"
            else:
                print("Invalid choice. Exiting.")
                return
        except Exception as e:
            print(f"❌ Error getting entity types: {e}")
            return
    elif choice == "3":
        # Analyze all entity types
        print("\nAnalyzing all entities for duplicates (this may take a while)...")
        duplicate_groups = identify_potential_duplicate_entities(graph, llm)
        analysis_type = "entity"
    else:
        print("Invalid choice. Exiting.")
        return
    
    if not duplicate_groups:
        print("\nNo potential duplicates identified. Nothing to resolve.")
        return
    
    # Step 2: Review and filter potential duplicates
    print(f"\nFound {len(duplicate_groups)} potential duplicate groups")
    
    # Display duplicate groups summary
    for i, group in enumerate(duplicate_groups):
        if analysis_type == "entity_type":
            print(f"\nGroup {i+1}: {', '.join(group.get('duplicate_types', []))}")
            print(f"Reasoning: {group.get('reasoning', 'No reasoning provided')}")
            print(f"Recommended merge: {group.get('merge_recommendation', {}).get('keep_type', 'Unknown')}")
        else:
            print(f"\nGroup {i+1}: {', '.join(group.get('duplicate_names', []))}")
            print(f"Type: {group.get('entity_type', 'Unknown')}")
            print(f"Reasoning: {group.get('reasoning', 'No reasoning provided')}")
            print(f"Confidence: {group.get('confidence', 'Unknown')}")
    
    # Ask which groups to include in resolution
    include_all = input("\nInclude all groups in resolution plan? (y/n): ").lower() == 'y'
    
    filtered_groups = []
    if include_all:
        filtered_groups = duplicate_groups
    else:
        # Let user select specific groups
        group_choices = input("\nEnter comma-separated group numbers to include (e.g., 1,3,5): ")
        try:
            selected_indices = [int(idx.strip()) - 1 for idx in group_choices.split(',')]
            for idx in selected_indices:
                if 0 <= idx < len(duplicate_groups):
                    filtered_groups.append(duplicate_groups[idx])
                else:
                    print(f"Warning: Group {idx + 1} is out of range, skipping")
        except Exception as e:
            print(f"Error parsing selection: {e}")
            print("Using all groups as fallback")
            filtered_groups = duplicate_groups
    
    if not filtered_groups:
        print("No groups selected for resolution. Exiting.")
        return
    
    print(f"\nCreating resolution plan for {len(filtered_groups)} groups...")
    
    # Step 3: Create resolution plan
    resolution_plan = create_resolution_plan(graph, llm, filtered_groups, analysis_type)
    resolution_plan = ensure_items_in_resolution_plan(resolution_plan, duplicate_groups, analysis_type)

    
    if not resolution_plan or not resolution_plan.get("groups"):
        print("Failed to create resolution plan. Exiting.")
        return
    
    # Save the plan
    save_resolution_plan(resolution_plan)
    
    # Display the plan
    print(format_resolution_plan_for_display(resolution_plan))
    
    # Step 4: Execute resolution
    review_plan = input("\nWould you like to review and execute this resolution plan? (y/n): ").lower() == 'y'
    
    if not review_plan:
        print("Resolution plan saved but not executed. Exiting.")
        return
    
    # Step 5: Create backup
    backup_prompt = input("\nCreate a database backup before proceeding? (recommended) (y/n): ").lower() == 'y'
    
    if backup_prompt:
        backup_success = backup_neo4j_database(container_name)
        if not backup_success:
            proceed_anyway = input("\nBackup failed. Proceed anyway? (y/n): ").lower() == 'y'
            if not proceed_anyway:
                print("Operation cancelled. Exiting.")
                return
    
    # Step 6: Execute plan - group by group
    for i, group in enumerate(resolution_plan.get("groups", [])):
        print(f"\n{'='*80}")
        print(f"GROUP {i+1}: {group.get('group_summary', 'Unknown')}")
        print(f"{'='*80}")
        
        execute_group = input(f"\nExecute resolution for group {i+1}? (y/n): ").lower() == 'y'
        
        if execute_group:
            execute_resolution_plan(graph, resolution_plan, i)
        else:
            print(f"Skipping group {i+1}")
    
    print("\n" + "="*80)
    print("DUPLICATE RESOLUTION WORKFLOW COMPLETED")
    print("="*80)


def main():
    parser = argparse.ArgumentParser(description="Neo4j Entity Duplicate Detection and Resolution")
    
    # Connection options
    parser.add_argument("--container", default="neo4j", help="Neo4j container name")
    
    # Processing options
    parser.add_argument("--model", default="llama3.1:latest", help="LLM model name")
    parser.add_argument("--temperature", type=float, default=0.1, help="LLM temperature")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    # Operation mode
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--entity-type", help="Analyze entities of a specific type")
    parser.add_argument("--analyze-labels", action="store_true", help="Analyze entity types (labels) for duplicates")
    parser.add_argument("--load-plan", help="Load and execute a previously saved resolution plan")
    
    # Automatic execution mode
    parser.add_argument("--execute", action="store_true", help="Execute the loaded resolution plan")
    parser.add_argument("--backup", action="store_true", help="Create a backup before executing resolution plan")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without executing changes")
    
    args = parser.parse_args()
    
    # Set up global verbosity
    global VERBOSE
    VERBOSE = args.verbose
    
    # Initialize Neo4j connection
    try:
        graph = initialize_neo4j_connection()
    except Exception as e:
        print(f"\nCould not connect to Neo4j: {e}")
        print("Please ensure Neo4j is running and credentials are correct.")
        return

    # Initialize LLM
    try:
        llm = initialize_llm(model_name=args.model, temperature=args.temperature)
    except Exception as e:
        print(f"\nCould not initialize LLM: {e}")
        print("Please ensure Ollama is running and the model is available.")
        return
    
    # Load and execute a previously saved plan
    if args.load_plan:
        try:
            with open(args.load_plan, 'r', encoding='utf-8') as f:
                resolution_plan = json.load(f)
            
            print(f"Loaded resolution plan from {args.load_plan}")
            print(format_resolution_plan_for_display(resolution_plan))

            execute_plan = args.execute
        
            if not execute_plan:
                # If --execute wasn't specified, ask for confirmation
                execute_plan = input("\nExecute this resolution plan? (y/n): ").lower() == 'y'
            
            if execute_plan:
                backup_needed = args.backup
                
                if not backup_needed:
                    # If --backup wasn't specified, ask for confirmation
                    backup_needed = input("\nCreate a database backup before proceeding? (recommended) (y/n): ").lower() == 'y'
                
                if backup_needed:
                    backup_success = backup_neo4j_database(args.container)
                    if not backup_success:
                        proceed_anyway = input("\nBackup failed. Proceed anyway? (y/n): ").lower() == 'y'
                        if not proceed_anyway:
                            print("Operation cancelled. Exiting.")
                            return
                
                # Add dry-run support
                if args.dry_run:
                    print("\n⚠️ DRY RUN MODE - showing operations that would be performed but not executing them")
                    # Here you could add code to show the operations without executing them
                    # For now, we'll just print a message
                    print(format_resolution_plan_for_display(resolution_plan))
                    print("\nDry run completed. No changes were made to the database.")
                    return
                
                # Execute the plan
                execute_resolution_plan(graph, resolution_plan)
            
            else:
                print("Resolution plan not executed. Exiting.")
            
            return
        except Exception as e:
            print(f"❌ Error loading resolution plan: {e}")
            return
    
    # Run in interactive mode
    if args.interactive:
        interactive_duplicate_resolution(graph, llm, args.container)
        return
    
    # Analyze entity types (labels)
    if args.analyze_labels:
        print("Analyzing entity types for duplicates...")
        duplicate_groups = identify_potential_duplicate_entity_types(graph, llm)
        
        if duplicate_groups:
            print(f"\nFound {len(duplicate_groups)} potential duplicate entity type groups")
            
            # Display duplicate groups
            for i, group in enumerate(duplicate_groups):
                print(f"\nGroup {i+1}: {', '.join(group.get('duplicate_types', []))}")
                print(f"Reasoning: {group.get('reasoning', 'No reasoning provided')}")
                print(f"Recommended merge: {group.get('merge_recommendation', {}).get('keep_type', 'Unknown')}")
            
            # Create resolution plan
            create_plan = input("\nCreate resolution plan for these duplicates? (y/n): ").lower() == 'y'
            
            if create_plan:
                resolution_plan = create_resolution_plan(graph, llm, duplicate_groups, "entity_type")
                resolution_plan = ensure_items_in_resolution_plan(resolution_plan, duplicate_groups, "entity_type")
                for group in resolution_plan.get("groups", []):
                    # Make sure items field matches the duplicate_types for entity_type duplicates
                    if not group.get("items"):
                        matching_dup_group = next((dg for dg in duplicate_groups if set(dg.get("duplicate_types", [])) == set(group.get("duplicate_types", []))), None)
                        if matching_dup_group:
                            group["items"] = matching_dup_group.get("duplicate_types", [])
                plan_path = save_resolution_plan(resolution_plan)
                print(format_resolution_plan_for_display(resolution_plan))
                
                # Add this new section to offer execution
                execute_now = input("\nExecute this resolution plan now? (y/n): ").lower() == 'y'
                if execute_now:
                    backup_prompt = input("\nCreate a database backup before proceeding? (recommended) (y/n): ").lower() == 'y'
                    if backup_prompt:
                        backup_success = backup_neo4j_database(args.container)
                        if not backup_success:
                            proceed_anyway = input("\nBackup failed. Proceed anyway? (y/n): ").lower() == 'y'
                            if not proceed_anyway:
                                print("Operation cancelled. Exiting.")
                                return
                    
                    # Execute the resolution plan
                    execute_resolution_plan(graph, resolution_plan)
        else:
            print("No potential duplicate entity types found")
        
        return
    
    # Analyze entities of a specific type
    if args.entity_type:
        print(f"Analyzing entities of type '{args.entity_type}' for duplicates...")
        duplicate_groups = identify_potential_duplicate_entities(graph, llm, args.entity_type)
        
        if duplicate_groups:
            print(f"\nFound {len(duplicate_groups)} potential duplicate groups")
            
            # Display duplicate groups
            for i, group in enumerate(duplicate_groups):
                print(f"\nGroup {i+1}: {', '.join(group.get('duplicate_names', []))}")
                print(f"Reasoning: {group.get('reasoning', 'No reasoning provided')}")
                print(f"Confidence: {group.get('confidence', 'Unknown')}")
            
            # Create resolution plan
            create_plan = input("\nCreate resolution plan for these duplicates? (y/n): ").lower() == 'y'
            
            if create_plan:
                resolution_plan = create_resolution_plan(graph, llm, duplicate_groups, "entity")
                resolution_plan = ensure_items_in_resolution_plan(resolution_plan, duplicate_groups, "entity")
                plan_path = save_resolution_plan(resolution_plan)
                print(format_resolution_plan_for_display(resolution_plan))
                
                # Add execution option
                execute_now = input("\nExecute this resolution plan now? (y/n): ").lower() == 'y'
                if execute_now:
                    backup_prompt = input("\nCreate a database backup before proceeding? (recommended) (y/n): ").lower() == 'y'
                    if backup_prompt:
                        backup_success = backup_neo4j_database(args.container)
                        if not backup_success:
                            proceed_anyway = input("\nBackup failed. Proceed anyway? (y/n): ").lower() == 'y'
                            if not proceed_anyway:
                                print("Operation cancelled. Exiting.")
                                return
                            
                    # Execute the resolution plan
                    execute_resolution_plan(graph, resolution_plan)
        else:
            print(f"No potential duplicate entities found for type '{args.entity_type}'")
        
        return
    
    # If we get here, no specific operation was requested
    print("No operation specified. Use --interactive, --analyze-labels, --entity-type, or --load-plan")
    print("Use --help for more information about available options")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()    