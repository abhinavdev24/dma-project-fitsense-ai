#!/usr/bin/env python3
"""
MongoDB Data Ingestion Script for FitSense AI

Ingests data from CSV files in ./data into MongoDB Atlas.
Schema is derived from the MySQL schema in database/mysql.sql.

Usage:
    python mongo_ingest.py                    # Ingest all collections
    python mongo_ingest.py --collections users # Ingest specific collections
    python mongo_ingest.py --reset            # Drop and recreate collections
    python mongo_ingest.py --dry-run           # Preview without inserting

Environment:
    Set MONGODB_PASSWORD in environment or .env file
"""

import argparse
import os
import re
import sys
import logging
from datetime import datetime, date
from pathlib import Path
from typing import Any, Optional

import pandas as pd
from pymongo import MongoClient, ASCENDING
from pymongo.errors import BulkWriteError
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# =============================================================================
# Configuration
# =============================================================================

# Load environment variables
load_dotenv()

# MongoDB Connection
mongodb_command = os.getenv("MONGODB_COMMAND", "")
# Extract URI from mongosh command format
uri_match = re.search(r'mongodb\+srv://[^\s"]+|mongodb://[^\s"]+', mongodb_command)
MONGODB_URI = (
    uri_match.group(0) if uri_match else "mongodb+srv://cluster0.bcgnj8a.mongodb.net/"
)

MONGODB_USER = os.getenv("MONGODB_USER", "abhinav241998_db_user")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD", "")
MONGODB_DATABASE = "fitsense_ai"

# Data directory
DATA_DIR = Path(__file__).parent.parent / "data"

# =============================================================================
# Collection Definitions
# =============================================================================

# Ordered list of collections for ingestion (respects foreign key dependencies)
COLLECTION_ORDER = [
    # Independent tables
    ("users", ["users.csv"]),
    ("goals", ["goals.csv"]),
    ("conditions", ["conditions.csv"]),
    ("equipment", ["equipment.csv"]),
    ("exercises", ["exercises.csv"]),
    # Junction tables with dependencies
    ("user_goals", ["user_goals.csv"]),
    ("user_conditions", ["user_conditions.csv"]),
    ("exercise_equipment", ["exercise_equipment.csv"]),
    # Workout plans
    ("workout_plans", ["workout_plans.csv"]),
    ("plan_days", ["plan_days.csv"]),
    ("plan_exercises", ["plan_exercises.csv"]),
    ("plan_sets", ["plan_sets.csv"]),
    # Workouts
    ("workouts", ["workouts.csv"]),
    ("workout_exercises", ["workout_exercises.csv"]),
    ("workout_sets", ["workout_sets.csv"]),
    # AI Interactions
    ("ai_interactions", ["ai_interactions.csv"]),
    # User Profiles
    ("user_profiles", ["user_profiles.csv"]),
    ("user_medical_profiles", ["user_medical_profiles.csv"]),
    ("user_medications", ["user_medications.csv"]),
    ("user_allergies", ["user_allergies.csv"]),
    # Calorie Tracking
    ("calorie_targets", ["calorie_targets.csv"]),
    ("calorie_intake_logs", ["calorie_intake_logs.csv"]),
    # Sleep Tracking
    ("sleep_targets", ["sleep_targets.csv"]),
    ("sleep_duration_logs", ["sleep_duration_logs.csv"]),
    # Weight Tracking
    ("weight_logs", ["weight_logs.csv"]),
]

# =============================================================================
# Utility Functions
# =============================================================================


def parse_datetime(value: Any) -> Optional[datetime]:
    """Parse datetime from various formats."""
    if pd.isna(value):
        return None

    if isinstance(value, datetime):
        return value

    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()

    value_str = str(value).strip()
    if not value_str:
        return None

    # Handle ISO format with timezone offset (e.g., 2025-10-21T00:00:00+00:00)
    if "+" in value_str or value_str.endswith("Z"):
        try:
            # Parse ISO format with timezone
            from dateutil import parser

            return parser.isoparse(value_str).replace(tzinfo=None)
        except Exception:
            pass

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value_str, fmt)
        except ValueError:
            continue

    logger.warning(f"Could not parse datetime: {value}")
    return None


def parse_date(value: Any) -> Optional[datetime]:
    """Parse date from various formats. Returns datetime for MongoDB compatibility."""
    if pd.isna(value):
        return None

    if isinstance(value, datetime):
        return value

    if isinstance(value, date) and not isinstance(value, datetime):
        # Convert date to datetime (MongoDB can't encode date directly)
        return datetime.combine(value, datetime.min.time())

    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()

    value_str = str(value).strip()
    if not value_str:
        return None

    formats = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"]

    for fmt in formats:
        try:
            dt = datetime.strptime(value_str, fmt)
            return dt
        except ValueError:
            continue

    logger.warning(f"Could not parse date: {value}")
    return None


def parse_uuid(value: Any) -> Optional[str]:
    """Parse UUID/binary from hex string or bytes."""
    if pd.isna(value):
        return None

    if isinstance(value, bytes):
        return value.hex()

    value_str = str(value).strip()
    if not value_str:
        return None

    # Remove any 0x prefix
    if value_str.startswith("0x") or value_str.startswith("0X"):
        value_str = value_str[2:]

    # Handle binary string representation
    if len(value_str) == 32:
        return value_str.lower()

    return value_str.lower()


def parse_boolean(value: Any) -> Optional[bool]:
    """Parse boolean from various representations."""
    if pd.isna(value):
        return None

    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return bool(int(value))

    value_str = str(value).strip().lower()
    if value_str in ("true", "1", "yes", "on"):
        return True
    if value_str in ("false", "0", "no", "off", ""):
        return False

    logger.warning(f"Could not parse boolean: {value}")
    return None


# Field type mappings (MySQL type patterns to converter functions)
FIELD_TYPE_MAPPINGS = {
    # UUID/Binary fields - stored as hex strings
    "uuid": lambda x: str(x).lower() if pd.notna(x) and str(x).strip() else None,
    # String fields
    "varchar": lambda x: str(x).strip() if pd.notna(x) and str(x).strip() else None,
    "text": lambda x: str(x).strip() if pd.notna(x) and str(x).strip() else None,
    "enum": lambda x: str(x).strip() if pd.notna(x) and str(x).strip() else None,
    # Integer fields
    "tinyint": lambda x: int(x) if pd.notna(x) else None,
    "smallint": lambda x: int(x) if pd.notna(x) else None,
    "mediumint": lambda x: int(x) if pd.notna(x) else None,
    # Float/Decimal fields
    "decimal": lambda x: float(x) if pd.notna(x) else None,
    "float": lambda x: float(x) if pd.notna(x) else None,
    # Boolean fields (TINYINT(1))
    "boolean": parse_boolean,
    # Datetime fields
    "datetime": parse_datetime,
    # Date fields
    "date": parse_date,
}


# Collection-specific field definitions based on MySQL schema
COLLECTION_FIELDS = {
    "users": {
        "user_id": "uuid",
        "name": "varchar",
        "email": "varchar",
        "created_at": "datetime",
    },
    "goals": {
        "goal_id": "uuid",
        "name": "varchar",
        "description": "text",
    },
    "user_goals": {
        "user_id": "uuid",
        "goal_id": "uuid",
        "priority": "tinyint",
    },
    "conditions": {
        "condition_id": "uuid",
        "name": "varchar",
        "description": "text",
    },
    "user_conditions": {
        "user_id": "uuid",
        "condition_id": "uuid",
        "severity": "enum",
        "notes": "text",
    },
    "equipment": {
        "equipment_id": "uuid",
        "name": "varchar",
        "category": "varchar",
    },
    "exercises": {
        "exercise_id": "uuid",
        "name": "varchar",
        "primary_muscle": "varchar",
        "notes": "text",
        "video_url": "varchar",
        "thumbnail_base64": "text",
    },
    "exercise_equipment": {
        "exercise_id": "uuid",
        "equipment_id": "uuid",
    },
    "workout_plans": {
        "plan_id": "uuid",
        "user_id": "uuid",
        "name": "varchar",
        "is_active": "boolean",
        "created_at": "datetime",
    },
    "plan_days": {
        "plan_day_id": "uuid",
        "plan_id": "uuid",
        "name": "varchar",
        "day_order": "tinyint",
        "notes": "text",
    },
    "plan_exercises": {
        "plan_exercise_id": "uuid",
        "plan_day_id": "uuid",
        "exercise_id": "uuid",
        "position": "smallint",
        "notes": "text",
    },
    "plan_sets": {
        "plan_set_id": "uuid",
        "plan_exercise_id": "uuid",
        "set_number": "tinyint",
        "target_reps": "tinyint",
        "target_weight": "decimal",
        "target_rir": "tinyint",
        "rest_seconds": "smallint",
    },
    "workouts": {
        "workout_id": "uuid",
        "user_id": "uuid",
        "plan_id": "uuid",
        "plan_day_id": "uuid",
        "started_at": "datetime",
        "ended_at": "datetime",
        "notes": "text",
    },
    "workout_exercises": {
        "workout_exercise_id": "uuid",
        "workout_id": "uuid",
        "exercise_id": "uuid",
        "plan_exercise_id": "uuid",
        "position": "smallint",
        "notes": "text",
    },
    "workout_sets": {
        "workout_set_id": "uuid",
        "workout_exercise_id": "uuid",
        "set_number": "tinyint",
        "reps": "tinyint",
        "weight": "decimal",
        "rir": "tinyint",
        "is_warmup": "boolean",
        "completed_at": "datetime",
    },
    "ai_interactions": {
        "ai_interaction_id": "uuid",
        "user_id": "uuid",
        "context_type": "varchar",
        "context_id": "uuid",
        "query_text": "text",
        "response_text": "text",
        "model_name": "varchar",
        "created_at": "datetime",
    },
    "user_profiles": {
        "user_id": "uuid",
        "date_of_birth": "date",
        "sex": "enum",
        "height_cm": "decimal",
        "activity_level": "enum",
        "updated_at": "datetime",
    },
    "user_medical_profiles": {
        "medical_profile_id": "uuid",
        "user_id": "uuid",
        "has_injuries": "boolean",
        "injury_details": "text",
        "surgeries_history": "text",
        "family_history": "text",
        "notes": "text",
        "updated_at": "datetime",
    },
    "user_medications": {
        "medication_id": "uuid",
        "user_id": "uuid",
        "medication_name": "varchar",
        "dosage": "varchar",
        "frequency": "varchar",
        "start_date": "date",
        "end_date": "date",
        "notes": "text",
    },
    "user_allergies": {
        "allergy_id": "uuid",
        "user_id": "uuid",
        "allergen": "varchar",
        "reaction": "varchar",
        "severity": "enum",
        "notes": "text",
    },
    "calorie_targets": {
        "calorie_target_id": "uuid",
        "user_id": "uuid",
        "maintenance_calories": "smallint",
        "method": "enum",
        "effective_from": "date",
        "effective_to": "date",
        "notes": "text",
        "created_at": "datetime",
    },
    "calorie_intake_logs": {
        "calorie_log_id": "uuid",
        "user_id": "uuid",
        "log_date": "date",
        "calories_consumed": "smallint",
        "notes": "text",
        "created_at": "datetime",
    },
    "sleep_targets": {
        "sleep_target_id": "uuid",
        "user_id": "uuid",
        "target_sleep_hours": "decimal",
        "effective_from": "date",
        "effective_to": "date",
        "notes": "text",
        "created_at": "datetime",
    },
    "sleep_duration_logs": {
        "sleep_log_id": "uuid",
        "user_id": "uuid",
        "log_date": "date",
        "sleep_duration_hours": "decimal",
        "notes": "text",
        "created_at": "datetime",
    },
    "weight_logs": {
        "weight_log_id": "uuid",
        "user_id": "uuid",
        "logged_at": "datetime",
        "weight_kg": "decimal",
        "body_fat_percentage": "decimal",
        "notes": "text",
    },
}


# =============================================================================
# MongoDB Client
# =============================================================================


class MongoDBClient:
    """MongoDB client wrapper for data ingestion."""

    def __init__(self, uri: str, username: str, password: str, database: str):
        """Initialize MongoDB client."""
        self.uri = uri
        self.username = username
        self.password = password
        self.database_name = database
        self.client = None
        self.db = None

    def connect(self) -> None:
        """Connect to MongoDB Atlas."""
        # Build connection URI with credentials if password provided
        if self.password:
            # Extract cluster from URI
            if "@" in self.uri:
                base_uri = self.uri.split("@")[1]
            else:
                base_uri = self.uri.replace("mongodb+srv://", "")

            full_uri = f"mongodb+srv://{self.username}:{self.password}@{base_uri}"
        else:
            full_uri = self.uri
            logger.warning("No MongoDB password provided. Connection may fail.")

        logger.info(f"Connecting to MongoDB: {self.database_name}")
        self.client = MongoClient(full_uri, serverSelectionTimeoutMS=10000)
        self.db = self.client[self.database_name]

        # Test connection
        try:
            self.client.admin.command("ping")
            logger.info("Successfully connected to MongoDB Atlas")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def disconnect(self) -> None:
        """Disconnect from MongoDB."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")

    def drop_collection(self, collection_name: str) -> None:
        """Drop a collection."""
        try:
            self.db[collection_name].drop()
            logger.info(f"Dropped collection: {collection_name}")
        except Exception as e:
            logger.warning(f"Could not drop collection {collection_name}: {e}")

    def drop_all_collections(self) -> None:
        """Drop all collections."""
        for collection_name, _ in COLLECTION_ORDER:
            self.drop_collection(collection_name)

    def get_collection_count(self, collection_name: str) -> int:
        """Get document count in a collection."""
        return self.db[collection_name].count_documents({})

    def create_indexes(self, collection_name: str) -> None:
        """Create indexes for a collection based on MySQL schema."""
        indexes = {
            "users": [("email", ASCENDING)],
            "goals": [("name", ASCENDING)],
            "conditions": [("name", ASCENDING)],
            "equipment": [("name", ASCENDING)],
            "exercises": [("name", ASCENDING)],
            "user_goals": [("user_id", ASCENDING), ("goal_id", ASCENDING)],
            "user_conditions": [("user_id", ASCENDING), ("condition_id", ASCENDING)],
            "exercise_equipment": [
                ("exercise_id", ASCENDING),
                ("equipment_id", ASCENDING),
            ],
            "workout_plans": [("user_id", ASCENDING)],
            "plan_days": [("plan_id", ASCENDING)],
            "plan_exercises": [("plan_day_id", ASCENDING), ("exercise_id", ASCENDING)],
            "plan_sets": [("plan_exercise_id", ASCENDING)],
            "workouts": [("user_id", ASCENDING), ("started_at", ASCENDING)],
            "workout_exercises": [("workout_id", ASCENDING)],
            "workout_sets": [("workout_exercise_id", ASCENDING)],
            "ai_interactions": [("user_id", ASCENDING), ("created_at", ASCENDING)],
            "user_profiles": [("user_id", ASCENDING)],
            "user_medical_profiles": [("user_id", ASCENDING)],
            "user_medications": [("user_id", ASCENDING)],
            "user_allergies": [("user_id", ASCENDING)],
            "calorie_targets": [("user_id", ASCENDING), ("effective_from", ASCENDING)],
            "calorie_intake_logs": [("user_id", ASCENDING), ("log_date", ASCENDING)],
            "sleep_targets": [("user_id", ASCENDING), ("effective_from", ASCENDING)],
            "sleep_duration_logs": [("user_id", ASCENDING), ("log_date", ASCENDING)],
            "weight_logs": [("user_id", ASCENDING), ("logged_at", ASCENDING)],
        }

        if collection_name in indexes:
            try:
                collection = self.db[collection_name]
                for index_fields in indexes[collection_name]:
                    collection.create_index([index_fields])
                logger.info(f"Created indexes for: {collection_name}")
            except Exception as e:
                logger.warning(f"Could not create indexes for {collection_name}: {e}")


# =============================================================================
# Data Ingestion
# =============================================================================


def load_csv(csv_path: Path) -> pd.DataFrame:
    """Load CSV file into DataFrame."""
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    logger.info(f"Loading CSV: {csv_path.name}")
    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    df = df.where(pd.notna(df), None)  # Convert NaN to None
    logger.info(f"  Loaded {len(df)} rows, {len(df.columns)} columns")
    return df


def convert_value(value: Any, field_type: str) -> Any:
    """Convert value based on field type."""
    if value is None:
        return None

    converter = FIELD_TYPE_MAPPINGS.get(field_type)
    if converter:
        try:
            return converter(value)
        except Exception as e:
            logger.warning(f"Conversion error for type {field_type}: {value} - {e}")
            return str(value)

    # Default: return as string
    return str(value) if value else None


def convert_row(row: pd.Series, field_definitions: dict) -> dict:
    """Convert a DataFrame row to a MongoDB document."""
    document = {}
    for field_name, field_type in field_definitions.items():
        if field_name in row.index:
            value = row[field_name]
            document[field_name] = convert_value(value, field_type)
    return document


def ingest_collection(
    client: MongoDBClient,
    collection_name: str,
    csv_filename: str,
    dry_run: bool = False,
) -> dict:
    """Ingest data from CSV into MongoDB collection."""
    csv_path = DATA_DIR / csv_filename

    if not csv_path.exists():
        logger.warning(f"CSV file not found for {collection_name}: {csv_path}")
        return {"status": "skipped", "count": 0}

    try:
        df = load_csv(csv_path)

        if df.empty:
            logger.info(f"Empty CSV for {collection_name}")
            return {"status": "success", "count": 0}

        field_defs = COLLECTION_FIELDS.get(collection_name, {})
        documents = []

        for _, row in df.iterrows():
            doc = convert_row(row, field_defs)
            # Remove None values to keep documents clean
            doc = {k: v for k, v in doc.items() if v is not None}
            documents.append(doc)

        if dry_run:
            logger.info(
                f"[DRY RUN] Would insert {len(documents)} documents into {collection_name}"
            )
            return {
                "status": "dry_run",
                "count": len(documents),
                "sample": documents[:3],
            }

        # Insert documents
        collection = client.db[collection_name]
        result = collection.insert_many(documents, ordered=False)

        # Create indexes
        client.create_indexes(collection_name)

        return {
            "status": "success",
            "count": len(result.inserted_ids),
        }

    except BulkWriteError as e:
        # Some documents may have been inserted despite errors
        inserted = e.details.get("nInserted", 0)
        logger.warning(
            f"Partial insert for {collection_name}: {inserted} inserted, errors occurred"
        )
        return {"status": "partial", "count": inserted, "errors": e.details}

    except Exception as e:
        logger.error(f"Error ingesting {collection_name}: {e}")
        return {"status": "error", "count": 0, "error": str(e)}


def ingest_all_collections(
    client: MongoDBClient,
    collections: Optional[list[str]] = None,
    dry_run: bool = False,
) -> dict:
    """Ingest all or specified collections."""
    results = {}

    # Filter collections if specified
    collections_to_ingest = []
    for collection_name, csv_files in COLLECTION_ORDER:
        if collections is None or collection_name in collections:
            collections_to_ingest.append((collection_name, csv_files[0]))

    if not collections_to_ingest:
        logger.warning("No collections to ingest")
        return results

    logger.info(f"Starting ingestion of {len(collections_to_ingest)} collections")
    logger.info("=" * 60)

    for collection_name, csv_filename in collections_to_ingest:
        logger.info(f"Processing: {collection_name}")
        result = ingest_collection(client, collection_name, csv_filename, dry_run)
        results[collection_name] = result

        status_icon = (
            "✓"
            if result["status"] == "success"
            else "⚠" if result["status"] == "partial" else "✗"
        )
        logger.info(
            f"  {status_icon} {result['status'].upper()}: {result['count']} documents"
        )

    logger.info("=" * 60)
    logger.info("Ingestion complete!")

    # Summary
    total_inserted = sum(r.get("count", 0) for r in results.values())
    successful = sum(1 for r in results.values() if r["status"] == "success")
    logger.info(f"Total documents inserted: {total_inserted}")
    logger.info(f"Successful collections: {successful}/{len(results)}")

    return results


def show_collection_preview(
    client: MongoDBClient,
    collection_name: str,
) -> None:
    """Show a preview of collection data (document count and sample)."""
    count = client.get_collection_count(collection_name)
    logger.info(f"\nCollection: {collection_name}")
    logger.info(f"  Document count: {count}")

    if count > 0:
        sample = list(client.db[collection_name].find().limit(3))
        for i, doc in enumerate(sample, 1):
            # Convert ObjectId to string for display
            doc_id = doc.pop("_id", None)
            logger.info(f"  Sample {i}: _id={str(doc_id) if doc_id else 'N/A'}")
            for key, value in list(doc.items())[:5]:
                value_str = (
                    str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                )
                logger.info(f"    {key}: {value_str}")
            if len(doc) > 5:
                logger.info(f"    ... and {len(doc) - 5} more fields")


def show_database_preview(client: MongoDBClient) -> None:
    """Show preview of all collections in the database."""
    logger.info("\n" + "=" * 60)
    logger.info(f"Database: {client.database_name}")
    logger.info("=" * 60)

    for collection_name, _ in COLLECTION_ORDER:
        show_collection_preview(client, collection_name)

    logger.info("=" * 60)


# =============================================================================
# CLI Interface
# =============================================================================


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="MongoDB Data Ingestion Script for FitSense AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                        # Ingest all collections
  %(prog)s --collections users goals  # Ingest specific collections
  %(prog)s --reset                 # Drop and recreate collections
  %(prog)s --dry-run               # Preview without inserting
  %(prog)s --preview              # Show existing data in database
  %(prog)s --password YOUR_PASS   # Provide MongoDB password

Environment:
  MONGODB_COMMAND   - MongoDB connection URI (from .env)
  MONGODB_USER      - MongoDB username (default: abhinav_db_user)
  MONGODB_PASSWORD  - MongoDB password
        """,
    )

    parser.add_argument(
        "--collections",
        "-c",
        nargs="+",
        help="Specific collections to ingest (default: all)",
    )
    parser.add_argument(
        "--reset",
        "-r",
        action="store_true",
        help="Drop all collections before ingesting",
    )
    parser.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        help="Preview data without inserting into MongoDB",
    )
    parser.add_argument(
        "--preview",
        "-p",
        action="store_true",
        help="Preview existing data in MongoDB (no changes)",
    )
    parser.add_argument(
        "--password",
        help="MongoDB password (or set MONGODB_PASSWORD env var)",
    )
    parser.add_argument(
        "--list-collections",
        "-l",
        action="store_true",
        help="List all available collections",
    )

    args = parser.parse_args()

    # Handle password
    if args.password:
        os.environ["MONGODB_PASSWORD"] = args.password

    # List collections
    if args.list_collections:
        print("\nAvailable collections:")
        for collection_name, csv_files in COLLECTION_ORDER:
            print(f"  - {collection_name} ({csv_files[0]})")
        return

    # Create MongoDB client
    try:
        client = MongoDBClient(
            uri=MONGODB_URI,
            username=MONGODB_USER,
            password=MONGODB_PASSWORD or os.getenv("MONGODB_PASSWORD", ""),
            database=MONGODB_DATABASE,
        )
        client.connect()
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        sys.exit(1)

    try:
        # Preview mode
        if args.preview:
            show_database_preview(client)
            return

        # Reset mode
        if args.reset:
            logger.warning("Dropping all collections...")
            client.drop_all_collections()
            logger.info("Collections dropped. Proceeding with ingestion...")

        # Dry run mode
        if args.dry_run:
            logger.info("DRY RUN MODE - No data will be inserted")

        # Validate collections
        if args.collections:
            valid_collections = {c[0] for c in COLLECTION_ORDER}
            invalid = set(args.collections) - valid_collections
            if invalid:
                logger.error(f"Invalid collections: {invalid}")
                logger.error(f"Valid collections: {sorted(valid_collections)}")
                sys.exit(1)

        # Ingest data
        results = ingest_all_collections(
            client,
            collections=args.collections,
            dry_run=args.dry_run,
        )

        # Exit with error if any failures
        errors = {k: v for k, v in results.items() if v["status"] == "error"}
        if errors:
            logger.error(f"\nFailed collections: {list(errors.keys())}")
            sys.exit(1)

    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
