"""
MongoDB Connection Utility for FitSense AI Dashboard
Handles MongoDB Atlas connection for NoSQL Explorer with read-only enforcement.

SECURITY NOTE: This utility enforces read-only access to MongoDB.
Write operations (insert, update, delete, drop, etc.) are blocked at the
application level for data protection.
"""

import os
import re
import time
from typing import Dict, List, Any, Optional
from contextlib import contextmanager
from dotenv import load_dotenv

import pandas as pd
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Load environment variables - prioritize .env.local over .env
load_dotenv()  # Load default .env first
load_dotenv('.env.local', override=True)  # Override with .env.local

# =============================================================================
# Configuration
# =============================================================================

# Parse MongoDB connection from MONGODB_COMMAND (full mongosh command or direct URI)
# .env provides: MONGODB_COMMAND=mongosh "mongodb+srv://cluster0.bcgnj8a.mongodb.net/" --apiVersion 1 --username abhinav241998_db_user
_mongodb_command = os.getenv("MONGODB_COMMAND", "")

if _mongodb_command:
    # Extract URI from mongosh command format (e.g., mongosh "mongodb+srv://cluster..." --username user)
    uri_match = re.search(r'mongodb\+srv://[^\s"]+|mongodb://[^\s"]+', _mongodb_command)
    if uri_match:
        MONGODB_URI = uri_match.group(0)
    else:
        # Treat as direct URI
        MONGODB_URI = _mongodb_command
else:
    MONGODB_URI = "mongodb+srv://cluster0.bcgnj8a.mongodb.net/"

MONGODB_USER = os.getenv("MONGODB_USER", "abhinav241998_db_user")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD", "")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "fitsense_ai")

# Write operations that should be blocked for read-only access
BLOCKED_OPERATIONS = [
    "insert", "insert_one", "insert_many", "update", "update_one", "update_many",
    "replace_one", "delete", "delete_one", "delete_many", "remove",
    "drop", "drop_collection", "drop_database", "collmod", "create", "createIndex",
    "deleteIndex", "aggregate_write", "bulk_write"
]

# =============================================================================
# MongoDB Client
# =============================================================================

_mongo_client: Optional[MongoClient] = None
_mongo_db = None


def get_mongo_uri() -> str:
    """Build MongoDB connection URI with credentials."""
    if MONGODB_PASSWORD:
        # Extract cluster from URI
        if "@" in MONGODB_URI:
            base_uri = MONGODB_URI.split("@")[1]
        else:
            base_uri = MONGODB_URI.replace("mongodb+srv://", "").replace("mongodb://", "")

        return f"mongodb+srv://{MONGODB_USER}:{MONGODB_PASSWORD}@{base_uri}"
    else:
        return MONGODB_URI


def get_mongo_client() -> MongoClient:
    """Get or create MongoDB client."""
    global _mongo_client
    if _mongo_client is None:
        uri = get_mongo_uri()
        _mongo_client = MongoClient(uri, serverSelectionTimeoutMS=10000)
    return _mongo_client


def get_mongo_database():
    """Get MongoDB database."""
    global _mongo_db
    if _mongo_db is None:
        client = get_mongo_client()
        _mongo_db = client[MONGODB_DATABASE]
    return _mongo_db


@contextmanager
def mongo_connection():
    """Context manager for MongoDB connections."""
    client = get_mongo_client()
    try:
        # Test connection
        client.admin.command('ping')
        yield get_mongo_database()
    except PyMongoError as e:
        raise ConnectionError(f"MongoDB connection failed: {e}")


# =============================================================================
# Read-Only Validation
# =============================================================================

def validate_readonly_operation(collection: str, operation: str) -> tuple:
    """
    Validate that the operation is read-only.
    
    Args:
        collection: Collection name
        operation: Operation being attempted
        
    Returns:
        (is_valid, error_message) tuple
    """
    operation_lower = operation.lower()
    
    for blocked_op in BLOCKED_OPERATIONS:
        if blocked_op in operation_lower:
            return False, f"Operation '{blocked_op}' is not allowed. This dashboard only supports read-only operations."
    
    return True, ""


# =============================================================================
# Query Execution
# =============================================================================

def execute_find(collection: str, query: Dict, projection: Dict = None, limit: int = 100) -> pd.DataFrame:
    """
    Execute a MongoDB find query and return results as a DataFrame.
    
    Args:
        collection: Collection name
        query: MongoDB query filter
        projection: Fields to include/exclude
        limit: Maximum number of documents
        
    Returns:
        DataFrame with query results
    """
    is_valid, error_msg = validate_readonly_operation(collection, "find")
    if not is_valid:
        raise ValueError(error_msg)
    
    db = get_mongo_database()
    coll = db[collection]
    
    cursor = coll.find(query, projection).limit(limit)
    results = list(cursor)
    
    # Convert ObjectId to string for JSON serialization
    for doc in results:
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
    
    return pd.DataFrame(results)


def execute_aggregation(collection: str, pipeline: List[Dict], limit: int = 100) -> pd.DataFrame:
    """
    Execute a MongoDB aggregation pipeline and return results as a DataFrame.
    
    Args:
        collection: Collection name
        pipeline: MongoDB aggregation pipeline
        limit: Maximum number of documents (applied as $limit at end)
        
    Returns:
        DataFrame with query results
    """
    # Validate pipeline doesn't contain write operations
    # Only check for MongoDB operators (starting with $) and method calls
    pipeline_str = str(pipeline)
    
    # Check for blocked method calls (find, aggregate with write intent)
    blocked_methods = ["insert", "update", "delete", "drop", "remove", "bulk_write", "createIndex", "deleteIndex"]
    for blocked_op in blocked_methods:
        if f".{blocked_op}(" in pipeline_str.lower():
            raise ValueError(f"Pipeline contains blocked operation '{blocked_op}()'. Only read operations are allowed.")
    
    # Check for blocked aggregation operators
    blocked_operators = ["$out", "$merge", "$collMod"]
    for blocked_op in blocked_operators:
        if blocked_op in pipeline_str:
            raise ValueError(f"Pipeline contains blocked operator '{blocked_op}'. Only read operations are allowed.")
    
    db = get_mongo_database()
    
    # Handle $listCollections special case
    if collection == "$listCollections":
        cursor = db.aggregate(pipeline)
    else:
        coll = db[collection]
        
        # Add limit at the end if not already present
        if limit > 0:
            has_limit = any("$limit" in str(stage) for stage in pipeline)
            if not has_limit:
                pipeline = pipeline + [{"$limit": limit}]
        
        cursor = coll.aggregate(pipeline)
    
    results = list(cursor)
    
    # Convert ObjectId to string for JSON serialization
    for doc in results:
        if "_id" in doc and hasattr(doc["_id"], "__str__"):
            doc["_id"] = str(doc["_id"])
    
    return pd.DataFrame(results)


def execute_query(query_data: Dict[str, Any]) -> tuple:
    """
    Execute a predefined NoSQL query and return results.
    
    Args:
        query_data: Dictionary containing 'collection' and 'pipeline' keys
        
    Returns:
        (DataFrame, execution_time) tuple
    """
    collection = query_data.get("collection")
    pipeline = query_data.get("pipeline", [])
    limit = query_data.get("limit", 100)
    
    start_time = time.time()
    
    if not pipeline:
        # Simple find query
        df = execute_find(collection, {}, limit=limit)
    else:
        # Aggregation pipeline
        df = execute_aggregation(collection, pipeline, limit=limit)
    
    exec_time = time.time() - start_time
    
    return df, exec_time


# =============================================================================
# Collection Info
# =============================================================================

def get_collection_counts() -> Dict[str, int]:
    """
    Get document counts for all collections.
    
    Returns:
        Dictionary mapping collection names to document counts
    """
    db = get_mongo_database()
    counts = {}
    
    for collection_name in db.list_collection_names():
        try:
            counts[collection_name] = db[collection_name].count_documents({})
        except PyMongoError:
            counts[collection_name] = 0
    
    return counts


def get_collection_sample(collection: str, limit: int = 3) -> List[Dict]:
    """
    Get sample documents from a collection.
    
    Args:
        collection: Collection name
        limit: Number of documents to return
        
    Returns:
        List of sample documents
    """
    db = get_mongo_database()
    coll = db[collection]
    
    cursor = coll.find().limit(limit)
    results = list(cursor)
    
    # Convert ObjectId to string
    for doc in results:
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
    
    return results


# =============================================================================
# Connection Testing
# =============================================================================

def test_connection() -> bool:
    """
    Test MongoDB connection.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        client = get_mongo_client()
        client.admin.command('ping')
        return True
    except Exception as e:
        print(f"MongoDB connection test failed: {e}")
        return False


def ensure_mongo_connection():
    """
    Ensure MongoDB connection is established for the current session.
    This function should be called at the beginning of any page that needs MongoDB access.
    It initializes session state and tests the connection silently.
    
    Note: Requires Streamlit (import streamlit as st) in the calling module.
    """
    import streamlit as st
    
    # Initialize session state if not present
    if "mongo_connected" not in st.session_state:
        st.session_state.mongo_connected = False
    
    # Test connection if not already connected
    if not st.session_state.mongo_connected:
        connected = test_connection()
        st.session_state.mongo_connected = connected
