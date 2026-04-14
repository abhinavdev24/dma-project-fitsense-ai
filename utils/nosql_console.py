"""
NoSQL Console Component for FitSense AI Dashboard
MongoDB query definitions organized by category.
"""

from typing import Dict, List, Tuple, Any

# =============================================================================
# BASIC FIND QUERIES (Simple Queries equivalent)
# =============================================================================

N1_ALL_USERS = {
    "collection": "users",
    "pipeline": [
        {"$sort": {"created_at": -1}},
        {"$limit": 50}
    ],
    "description": "Retrieve all users sorted by creation date"
}

N2_ALL_EXERCISES = {
    "collection": "exercises",
    "pipeline": [
        {"$sort": {"name": 1}},
        {"$limit": 50}
    ],
    "description": "Retrieve all exercises sorted by name"
}

N3_ALL_GOALS = {
    "collection": "goals",
    "pipeline": [],
    "description": "Retrieve all fitness goals"
}

N4_RECENT_WORKOUTS = {
    "collection": "workouts",
    "pipeline": [
        {"$match": {"started_at": {"$gte": {"$dateSubtract": {"startDate": "$$NOW", "amount": 30, "unit": "day"}}}}},
        {"$sort": {"started_at": -1}},
        {"$limit": 50}
    ],
    "description": "Retrieve workouts from the last 30 days"
}

# =============================================================================
# AGGREGATION QUERIES
# =============================================================================

A1_USERS_BY_ACTIVITY_LEVEL = {
    "collection": "user_profiles",
    "pipeline": [
        {"$group": {"_id": "$activity_level", "total": {"$sum": 1}}},
        {"$sort": {"total": -1}}
    ],
    "description": "Group users by activity level"
}

A2_USERS_BY_SEX = {
    "collection": "user_profiles",
    "pipeline": [
        {"$group": {"_id": "$sex", "total": {"$sum": 1}}},
        {"$sort": {"total": -1}}
    ],
    "description": "Group users by sex"
}

A3_AVG_HEIGHT_BY_SEX = {
    "collection": "user_profiles",
    "pipeline": [
        {"$match": {"height_cm": {"$ne": None}}},
        {"$group": {"_id": "$sex", "avg_height": {"$avg": "$height_cm"}}},
        {"$sort": {"_id": 1}}
    ],
    "description": "Calculate average height by sex"
}

A4_AGE_DISTRIBUTION = {
    "collection": "user_profiles",
    "pipeline": [
        {"$match": {"date_of_birth": {"$ne": None}}},
        {"$project": {
            "age": {
                "$floor": {
                    "$divide": [
                        {"$subtract": [{"$$NOW": "$date_of_birth"}, 31536000000]}
                    ]
                }
            }
        }},
        {"$bucket": {
            "groupBy": "$age",
            "boundaries": [0, 20, 30, 40, 50, 60, 150],
            "default": "60+",
            "output": {"count": {"$sum": 1}}
        }}
    ],
    "description": "Distribution of user ages"
}

A5_WORKOUTS_PER_DAY = {
    "collection": "workouts",
    "pipeline": [
        {"$match": {"started_at": {"$ne": None}}},
        {"$group": {
            "_id": {"$dayOfWeek": "$started_at"},
            "day_name": {"$first": {"$arrayElemAt": [["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"], {"$subtract": [{"$dayOfWeek": "$started_at"}, 1]}]}},
            "total": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ],
    "description": "Count workouts by day of week"
}

A6_MOST_POPULAR_GOALS = {
    "collection": "user_goals",
    "pipeline": [
        {"$lookup": {"from": "goals", "localField": "goal_id", "foreignField": "goal_id", "as": "goal"}},
        {"$unwind": "$goal"},
        {"$group": {"_id": "$goal.name", "total_users": {"$sum": 1}}},
        {"$sort": {"total_users": -1}}
    ],
    "description": "Most popular fitness goals"
}

A7_CONDITIONS_BY_SEVERITY = {
    "collection": "user_conditions",
    "pipeline": [
        {"$group": {"_id": "$severity", "total": {"$sum": 1}}},
        {"$sort": {"total": -1}}
    ],
    "description": "Count conditions by severity"
}

A8_AVG_WORKOUT_DURATION = {
    "collection": "workouts",
    "pipeline": [
        {"$match": {"started_at": {"$ne": None}, "ended_at": {"$ne": None}}},
        {"$lookup": {"from": "users", "localField": "user_id", "foreignField": "user_id", "as": "user"}},
        {"$unwind": "$user"},
        {"$project": {
            "name": "$user.name",
            "duration_mins": {"$divide": [{"$subtract": ["$ended_at", "$started_at"]}, 60000]}
        }},
        {"$group": {"_id": "$name", "avg_mins": {"$avg": "$duration_mins"}}},
        {"$sort": {"avg_mins": -1}},
        {"$limit": 20}
    ],
    "description": "Average workout duration by user"
}

# =============================================================================
# LOOKUP (JOIN equivalent) QUERIES
# =============================================================================

J1_USER_PROFILES_DEMOGRAPHICS = {
    "collection": "users",
    "pipeline": [
        {"$lookup": {"from": "user_profiles", "localField": "user_id", "foreignField": "user_id", "as": "profile"}},
        {"$unwind": {"path": "$profile", "preserveNullAndEmptyArrays": True}},
        {"$project": {
            "name": 1,
            "email": 1,
            "date_of_birth": "$profile.date_of_birth",
            "sex": "$profile.sex",
            "height_cm": "$profile.height_cm",
            "activity_level": "$profile.activity_level",
            "age": {"$floor": {"$divide": [{"$subtract": [{"$$NOW": "$profile.date_of_birth"}, 31536000000]}, 365.25]}}
        }},
        {"$sort": {"age": -1}},
        {"$limit": 50}
    ],
    "description": "User demographics with profiles"
}

J2_MOST_USED_EXERCISES = {
    "collection": "plan_exercises",
    "pipeline": [
        {"$lookup": {"from": "exercises", "localField": "exercise_id", "foreignField": "exercise_id", "as": "exercise"}},
        {"$unwind": "$exercise"},
        {"$group": {"_id": "$exercise.name", "times_programmed": {"$sum": 1}}},
        {"$sort": {"times_programmed": -1}},
        {"$limit": 10}
    ],
    "description": "Most frequently programmed exercises"
}

J3_TOP_ACTIVE_USERS = {
    "collection": "workouts",
    "pipeline": [
        {"$lookup": {"from": "users", "localField": "user_id", "foreignField": "user_id", "as": "user"}},
        {"$unwind": "$user"},
        {"$group": {"_id": "$user.name", "total_workouts": {"$sum": 1}}},
        {"$sort": {"total_workouts": -1}},
        {"$limit": 10}
    ],
    "description": "Users with most completed workouts"
}

J4_USERS_WITH_SEVERE_CONDITIONS = {
    "collection": "user_conditions",
    "pipeline": [
        {"$match": {"severity": "severe"}},
        {"$lookup": {"from": "users", "localField": "user_id", "foreignField": "user_id", "as": "user"}},
        {"$lookup": {"from": "conditions", "localField": "condition_id", "foreignField": "condition_id", "as": "condition"}},
        {"$unwind": "$user"},
        {"$unwind": "$condition"},
        {"$project": {"name": "$user.name", "email": "$user.email", "condition_name": "$condition.name"}},
        {"$sort": {"name": 1}}
    ],
    "description": "Users with severe medical conditions"
}

# =============================================================================
# LOOKUP WITH MISSING DATA (OUTER JOIN equivalent)
# =============================================================================

O1_USERS_WITH_NO_GOALS = {
    "collection": "users",
    "pipeline": [
        {"$lookup": {"from": "user_goals", "localField": "user_id", "foreignField": "user_id", "as": "goals"}},
        {"$match": {"goals": {"$size": 0}}},
        {"$project": {"name": 1, "email": 1, "_id": 0}}
    ],
    "description": "Users who have not set any goals"
}

O2_USERS_WITH_NO_WORKOUTS = {
    "collection": "users",
    "pipeline": [
        {"$lookup": {"from": "workouts", "localField": "user_id", "foreignField": "user_id", "as": "workouts"}},
        {"$match": {"workouts": {"$size": 0}}},
        {"$project": {"name": 1, "email": 1, "_id": 0}}
    ],
    "description": "Users who have not completed any workouts"
}

O3_EXERCISES_NEVER_USED = {
    "collection": "exercises",
    "pipeline": [
        {"$lookup": {"from": "plan_exercises", "localField": "exercise_id", "foreignField": "exercise_id", "as": "usage"}},
        {"$match": {"usage": {"$size": 0}}},
        {"$project": {"name": 1, "primary_muscle": 1, "_id": 0}}
    ],
    "description": "Exercises that have never been programmed"
}

# =============================================================================
# NESTED SUBQUERIES (MongoDB aggregation equivalent)
# =============================================================================

N_SUB1_USERS_ABOVE_AVERAGE_WORKOUTS = {
    "collection": "workouts",
    "pipeline": [
        {"$group": {"_id": "$user_id", "total_workouts": {"$sum": 1}}},
        {"$group": {"_id": None, "avg_count": {"$avg": "$total_workouts"}, "user_counts": {"$push": {"user_id": "$_id", "count": "$total_workouts"}}}},
        {"$unwind": "$user_counts"},
        {"$match": {"$expr": {"$gt": ["$user_counts.count", "$avg_count"]}}},
        {"$lookup": {"from": "users", "localField": "user_counts.user_id", "foreignField": "user_id", "as": "user"}},
        {"$unwind": "$user"},
        {"$project": {"name": "$user.name", "total_workouts": "$user_counts.count"}},
        {"$sort": {"total_workouts": -1}}
    ],
    "description": "Users with more workouts than average"
}

N_SUB2_HEAVIEST_LIFTS_ABOVE_AVG = {
    "collection": "workout_sets",
    "pipeline": [
        {"$match": {"weight": {"$ne": None}}},
        {"$group": {"_id": None, "avg_weight": {"$avg": "$weight"}}},
        {"$lookup": {
            "from": "workout_sets",
            "pipeline": [
                {"$match": {"weight": {"$ne": None}}},
                {"$project": {"workout_set_id": 1, "weight": 1, "reps": 1, "above_avg": {"$gt": ["$weight", {"$literal": 0}]}}}
            ],
            "as": "sets"
        }},
        {"$unwind": "$sets"},
        {"$replaceRoot": {"newRoot": "$sets"}}
    ],
    "description": "Workout sets with weight above average"
}

# =============================================================================
# SET OPERATIONS (UNION equivalent)
# =============================================================================

U1_COLLECTION_COUNTS = {
    "collection": "$listCollections",
    "pipeline": [
        {"$listMongoThreads": True}
    ],
    "description": "Document counts across all collections"
}

U2_USERS_WITH_GOALS_OR_CONDITIONS = {
    "collection": "users",
    "pipeline": [
        {"$lookup": {"from": "user_goals", "localField": "user_id", "foreignField": "user_id", "as": "goals"}},
        {"$lookup": {"from": "user_conditions", "localField": "user_id", "foreignField": "user_id", "as": "conditions"}},
        {"$match": {"$or": [{"goals": {"$ne": []}}, {"conditions": {"$ne": []}}]}},
        {"$project": {"user_id": 1, "name": 1, "has_goal": {"$cond": [{"$gt": [{"$size": "$goals"}, 0]}, "Yes", "No"]}, "has_condition": {"$cond": [{"$gt": [{"$size": "$conditions"}, 0]}, "Yes", "No"]}}},
        {"$limit": 50}
    ],
    "description": "Users with goals or medical conditions"
}

U3_COMBINED_TRACKING_DATA = {
    "collection": "calorie_intake_logs",
    "pipeline": [
        {"$project": {"user_id": 1, "log_date": 1, "metric": {"$literal": "calories"}, "value": "$calories_consumed"}},
        {"$unionWith": {"coll": "sleep_duration_logs", "pipeline": [{"$project": {"user_id": 1, "log_date": "$log_date", "metric": {"$literal": "sleep"}, "value": "$sleep_duration_hours"}}]}},
        {"$sort": {"log_date": -1}},
        {"$limit": 100}
    ],
    "description": "Combined calorie and sleep tracking data"
}

# =============================================================================
# SUBQUERIES IN MATCH
# =============================================================================

SM1_USER_SUMMARY = {
    "collection": "users",
    "pipeline": [
        {"$lookup": {"from": "workouts", "localField": "user_id", "foreignField": "user_id", "as": "workouts"}},
        {"$lookup": {"from": "user_goals", "localField": "user_id", "foreignField": "user_id", "as": "goals"}},
        {"$lookup": {"from": "weight_logs", "localField": "user_id", "foreignField": "user_id", "as": "weights"}},
        {"$project": {
            "name": 1,
            "email": 1,
            "workout_count": {"$size": "$workouts"},
            "goal_count": {"$size": "$goals"},
            "avg_weight": {"$avg": "$weights.weight_kg"}
        }},
        {"$sort": {"workout_count": -1}}
    ],
    "description": "User summary with workout and goal counts"
}

SM2_AVG_WORKOUTS_PER_USER = {
    "collection": "workouts",
    "pipeline": [
        {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
        {"$group": {"_id": None, "avg_workouts": {"$avg": "$count"}}},
        {"$project": {"avg_workouts_per_user": {"$round": ["$avg_workouts", 1]}}}
    ],
    "description": "Average number of workouts per user"
}

SM3_ACTIVITY_LEVEL_WITH_PERCENTAGE = {
    "collection": "user_profiles",
    "pipeline": [
        {"$group": {"_id": "$activity_level", "total": {"$sum": 1}}},
        {"$group": {"_id": None, "counts": {"$push": {"level": "$_id", "count": "$total"}}, "total_users": {"$sum": "$total"}}},
        {"$unwind": "$counts"},
        {"$project": {
            "activity_level": "$counts.level",
            "count": "$counts.count",
            "percentage": {"$multiply": [{"$divide": [{"$indexToArray": "$counts.count"}, {"$literal": 1}]}, {"$divide": ["$counts.count", "$total_users"]}, 100]}
        }},
        {"$sort": {"count": -1}}
    ],
    "description": "Activity level distribution with percentages"
}

# =============================================================================
# QUERY METADATA
# =============================================================================

QUERY_METADATA: Dict[str, Dict[str, str]] = {
    # Basic Find
    'N1': {'name': 'All Users', 'type': 'Basic Find', 'page': 'Users'},
    'N2': {'name': 'All Exercises', 'type': 'Basic Find', 'page': 'Workouts'},
    'N3': {'name': 'All Goals', 'type': 'Basic Find', 'page': 'Overview'},
    'N4': {'name': 'Recent Workouts', 'type': 'Basic Find', 'page': 'Overview'},
    # Aggregations
    'A1': {'name': 'Users by Activity Level', 'type': 'Aggregation', 'page': 'Users'},
    'A2': {'name': 'Users by Sex', 'type': 'Aggregation', 'page': 'Users'},
    'A3': {'name': 'Avg Height by Sex', 'type': 'Aggregation', 'page': 'Users'},
    'A4': {'name': 'Age Distribution', 'type': 'Aggregation', 'page': 'Users'},
    'A5': {'name': 'Workouts per Day of Week', 'type': 'Aggregation', 'page': 'Workouts'},
    'A6': {'name': 'Most Popular Goals', 'type': 'Aggregation + Lookup', 'page': 'Overview'},
    'A7': {'name': 'Conditions by Severity', 'type': 'Aggregation', 'page': 'Overview'},
    'A8': {'name': 'Avg Workout Duration', 'type': 'Aggregation + Lookup', 'page': 'Workouts'},
    # Lookups
    'J1': {'name': 'User Demographics', 'type': 'Lookup', 'page': 'Users'},
    'J2': {'name': 'Most Used Exercises', 'type': 'Lookup', 'page': 'Workouts'},
    'J3': {'name': 'Top Active Users', 'type': 'Lookup', 'page': 'Overview'},
    'J4': {'name': 'Users with Severe Conditions', 'type': 'Lookup', 'page': 'Users'},
    # Outer Lookup
    'O1': {'name': 'Users with No Goals', 'type': 'Outer Lookup', 'page': 'Overview'},
    'O2': {'name': 'Users with No Workouts', 'type': 'Outer Lookup', 'page': 'Overview'},
    'O3': {'name': 'Exercises Never Used', 'type': 'Outer Lookup', 'page': 'Workouts'},
    # Nested
    'NS1': {'name': 'Users Above Avg Workouts', 'type': 'Nested Aggregation', 'page': 'Workouts'},
    'NS2': {'name': 'Heaviest Lifts Above Avg', 'type': 'Nested Aggregation', 'page': 'Workouts'},
    # Union
    'U1': {'name': 'Collection Counts', 'type': 'Union', 'page': 'Overview'},
    'U2': {'name': 'Users with Goals OR Conditions', 'type': 'Union', 'page': 'Users'},
    'U3': {'name': 'Combined Tracking Data', 'type': 'Union', 'page': 'Nutrition'},
    # Subqueries
    'SM1': {'name': 'User Summary', 'type': 'Subquery', 'page': 'Overview'},
    'SM2': {'name': 'Avg Workouts Per User', 'type': 'Subquery', 'page': 'Overview'},
    'SM3': {'name': 'Activity Level with %', 'type': 'Subquery', 'page': 'Users'},
}

# =============================================================================
# QUERY CATEGORIES FOR UI
# =============================================================================

QUERY_CATEGORIES: Dict[str, List[str]] = {
    'Basic Find': ['N1', 'N2', 'N3', 'N4'],
    'Aggregation': ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8'],
    'Lookup (JOIN)': ['J1', 'J2', 'J3', 'J4'],
    'Outer Lookup': ['O1', 'O2', 'O3'],
    'Nested Aggregations': ['NS1', 'NS2'],
    'Set Operations (UNION)': ['U1', 'U2', 'U3'],
    'Subqueries': ['SM1', 'SM2', 'SM3'],
}

# =============================================================================
# QUERY LOOKUP DICTIONARY
# =============================================================================

QUERIES: Dict[str, Dict[str, Any]] = {
    # Basic Find
    'N1': N1_ALL_USERS,
    'N2': N2_ALL_EXERCISES,
    'N3': N3_ALL_GOALS,
    'N4': N4_RECENT_WORKOUTS,
    # Aggregations
    'A1': A1_USERS_BY_ACTIVITY_LEVEL,
    'A2': A2_USERS_BY_SEX,
    'A3': A3_AVG_HEIGHT_BY_SEX,
    'A4': A4_AGE_DISTRIBUTION,
    'A5': A5_WORKOUTS_PER_DAY,
    'A6': A6_MOST_POPULAR_GOALS,
    'A7': A7_CONDITIONS_BY_SEVERITY,
    'A8': A8_AVG_WORKOUT_DURATION,
    # Lookups
    'J1': J1_USER_PROFILES_DEMOGRAPHICS,
    'J2': J2_MOST_USED_EXERCISES,
    'J3': J3_TOP_ACTIVE_USERS,
    'J4': J4_USERS_WITH_SEVERE_CONDITIONS,
    # Outer Lookup
    'O1': O1_USERS_WITH_NO_GOALS,
    'O2': O2_USERS_WITH_NO_WORKOUTS,
    'O3': O3_EXERCISES_NEVER_USED,
    # Nested
    'NS1': N_SUB1_USERS_ABOVE_AVERAGE_WORKOUTS,
    'NS2': N_SUB2_HEAVIEST_LIFTS_ABOVE_AVG,
    # Union
    'U1': U1_COLLECTION_COUNTS,
    'U2': U2_USERS_WITH_GOALS_OR_CONDITIONS,
    'U3': U3_COMBINED_TRACKING_DATA,
    # Subqueries
    'SM1': SM1_USER_SUMMARY,
    'SM2': SM2_AVG_WORKOUTS_PER_USER,
    'SM3': SM3_ACTIVITY_LEVEL_WITH_PERCENTAGE,
}


def get_all_queries() -> Dict[str, Dict[str, Any]]:
    """Return all queries as a dictionary."""
    return QUERIES.copy()


def get_query_by_id(query_id: str) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """
    Get a query by its ID.
    Returns (query_data, metadata) tuple or (None, None) if not found.
    """
    query = QUERIES.get(query_id)
    metadata = QUERY_METADATA.get(query_id)
    return query, metadata


def get_collection_names() -> List[str]:
    """Get list of all MongoDB collection names."""
    return [
        "users", "goals", "conditions", "equipment", "exercises",
        "user_goals", "user_conditions", "exercise_equipment",
        "workout_plans", "plan_days", "plan_exercises", "plan_sets",
        "workouts", "workout_exercises", "workout_sets",
        "ai_interactions", "user_profiles", "user_medical_profiles",
        "user_medications", "user_allergies", "calorie_targets",
        "calorie_intake_logs", "sleep_targets", "sleep_duration_logs",
        "weight_logs"
    ]
