# FitSense AI - NoSQL Queries Reference

This document provides examples of different MongoDB aggregation query types used in the FitSense AI Dashboard.

---

## 1. Basic Find Queries

Simple queries equivalent to SQL `SELECT` statements - retrieving documents from a single collection.

### All Users

```javascript
db.users.find({}).limit(50)
```

**MongoDB Aggregation Equivalent:**
```javascript
db.users.aggregate([
    {"$sort": {"created_at": -1}},
    {"$limit": 50}
])
```

**Description:** Retrieves all users with their basic information, ordered by creation date.

---

### All Exercises

```javascript
db.exercises.find({}).limit(50)
```

**MongoDB Aggregation Equivalent:**
```javascript
db.exercises.aggregate([
    {"$sort": {"name": 1}},
    {"$limit": 50}
])
```

**Description:** Retrieves all exercises sorted alphabetically by name.

---

### Recent Workouts

```javascript
db.workouts.find({
    "started_at": {"$gte": new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)}
}).limit(50)
```

**MongoDB Aggregation Equivalent:**
```javascript
db.workouts.aggregate([
    {"$match": {"started_at": {"$gte": {"$dateSubtract": {"startDate": "$$NOW", "amount": 30, "unit": "day"}}}}},
    {"$sort": {"started_at": -1}},
    {"$limit": 50}
])
```

**Description:** Retrieves workouts from the last 30 days, sorted by date descending.

---

## 2. Aggregation Queries

Queries using `$group` with accumulator operators like `$sum`, `$avg`, equivalent to SQL `GROUP BY`.

### Users by Activity Level

```javascript
db.user_profiles.aggregate([
    {"$group": {"_id": "$activity_level", "total": {"$sum": 1}}},
    {"$sort": {"total": -1}}
])
```

**Description:** Groups users by their activity level and counts them.

**SQL Equivalent:**
```sql
SELECT activity_level, COUNT(*) AS total
FROM user_profiles
GROUP BY activity_level
ORDER BY total DESC
```

---

### Average Height by Sex

```javascript
db.user_profiles.aggregate([
    {"$match": {"height_cm": {"$ne": null}}},
    {"$group": {"_id": "$sex", "avg_height": {"$avg": "$height_cm"}}},
    {"$sort": {"_id": 1}}
])
```

**Description:** Calculates the average height for each sex.

**SQL Equivalent:**
```sql
SELECT sex, AVG(height_cm) AS avg_height
FROM user_profiles
WHERE height_cm IS NOT NULL
GROUP BY sex
ORDER BY sex
```

---

### Age Distribution

```javascript
db.user_profiles.aggregate([
    {"$match": {"date_of_birth": {"$ne": null}}},
    {"$project": {
        "age": {"$floor": {"$divide": [{"$subtract": [{"$$NOW": "$date_of_birth"}, 31536000000]}, 365.25]}}
    }},
    {"$bucket": {
        "groupBy": "$age",
        "boundaries": [0, 20, 30, 40, 50, 60, 150],
        "default": "60+",
        "output": {"count": {"$sum": 1}}
    }}
])
```

**Description:** Groups users into age brackets (0-19, 20-29, 30-39, 40-49, 50-59, 60+).

---

### Workouts per Day of Week

```javascript
db.workouts.aggregate([
    {"$match": {"started_at": {"$ne": null}}},
    {"$group": {
        "_id": {"$dayOfWeek": "$started_at"},
        "day_name": {"$first": {"$arrayElemAt": [["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"], {"$subtract": [{"$dayOfWeek": "$started_at"}, 1]}]}},
        "total": {"$sum": 1}
    }},
    {"$sort": {"_id": 1}}
])
```

**Description:** Counts workouts grouped by day of the week.

**SQL Equivalent:**
```sql
SELECT DAYNAME(started_at) AS day_name, COUNT(*) AS total
FROM workouts
WHERE started_at IS NOT NULL
GROUP BY DAYOFWEEK(started_at), DAYNAME(started_at)
ORDER BY DAYOFWEEK(started_at)
```

---

## 3. Lookup (JOIN) Queries

Queries using `$lookup` to join collections, equivalent to SQL `INNER JOIN`.

### User Demographics

```javascript
db.users.aggregate([
  { $lookup: { from: "user_profiles", localField: "user_id", foreignField: "user_id", as: "profile" } },
  { $unwind: { path: "$profile", preserveNullAndEmptyArrays: true } },
  { $project: {
      name: 1,
      email: 1,
      date_of_birth: "$profile.date_of_birth",
      sex: "$profile.sex",
      height_cm: "$profile.height_cm",
      activity_level: "$profile.activity_level",
      age: {
        $floor: {
          $divide: [
            { $subtract: ["$$NOW", "$profile.date_of_birth"] },
            31536000000
          ]
        }
      }
    }
  },
  { $sort: { age: -1 } },
  { $limit: 50 }
])
```

**Description:** Joins users with their profiles to create a demographic view.

**SQL Equivalent:**
```sql
SELECT u.name, u.email, p.date_of_birth, p.sex, p.height_cm, p.activity_level
FROM users u
JOIN user_profiles p ON u.user_id = p.user_id
ORDER BY p.date_of_birth DESC
LIMIT 50
```

---

### Top Active Users

```javascript
db.workouts.aggregate([
    {"$lookup": {"from": "users", "localField": "user_id", "foreignField": "user_id", "as": "user"}},
    {"$unwind": "$user"},
    {"$group": {"_id": "$user.name", "total_workouts": {"$sum": 1}}},
    {"$sort": {"total_workouts": -1}},
    {"$limit": 10}
])
```

**Description:** Finds users with the most completed workouts.

**SQL Equivalent:**
```sql
SELECT u.name, COUNT(*) AS total_workouts
FROM workouts w
JOIN users u ON w.user_id = u.user_id
GROUP BY u.name
ORDER BY total_workouts DESC
LIMIT 10
```

---

### Most Used Exercises

```javascript
db.plan_exercises.aggregate([
    {"$lookup": {"from": "exercises", "localField": "exercise_id", "foreignField": "exercise_id", "as": "exercise"}},
    {"$unwind": "$exercise"},
    {"$group": {"_id": "$exercise.name", "times_programmed": {"$sum": 1}}},
    {"$sort": {"times_programmed": -1}},
    {"$limit": 10}
])
```

**Description:** Counts how many times each exercise has been programmed in workout plans.

---

## 4. Outer Lookup (LEFT JOIN) Queries

Queries using `$lookup` with `$match` for `$size: 0` to find documents without related records, equivalent to SQL `LEFT JOIN ... WHERE ... IS NULL`.

### Users with No Goals

```javascript
db.users.aggregate([
    {"$lookup": {"from": "user_goals", "localField": "user_id", "foreignField": "user_id", "as": "goals"}},
    {"$match": {"goals": {"$size": 0}}},
    {"$project": {"name": 1, "email": 1, "_id": 0}}
])
```

**Description:** Finds users who have not set any fitness goals.

**SQL Equivalent:**
```sql
SELECT u.name, u.email
FROM users u
LEFT JOIN user_goals ug ON u.user_id = ug.user_id
WHERE ug.user_id IS NULL
```

---

### Users with No Workouts

```javascript
db.users.aggregate([
    {"$lookup": {"from": "workouts", "localField": "user_id", "foreignField": "user_id", "as": "workouts"}},
    {"$match": {"workouts": {"$size": 0}}},
    {"$project": {"name": 1, "email": 1, "_id": 0}}
])
```

**Description:** Finds users who have not completed any workouts.

---

### Exercises Never Used

```javascript
db.exercises.aggregate([
    {"$lookup": {"from": "plan_exercises", "localField": "exercise_id", "foreignField": "exercise_id", "as": "usage"}},
    {"$match": {"usage": {"$size": 0}}},
    {"$project": {"name": 1, "primary_muscle": 1, "_id": 0}}
])
```

**Description:** Finds exercises that have never been added to any workout plan.

---

## 5. Nested Aggregation Queries

Complex multi-stage aggregation pipelines with sub-aggregations, equivalent to SQL nested subqueries.

### Users with Above Average Workouts

```javascript
db.workouts.aggregate([
    {"$group": {"_id": "$user_id", "total_workouts": {"$sum": 1}}},
    {"$group": {"_id": null, "avg_count": {"$avg": "$total_workouts"}, "user_counts": {"$push": {"user_id": "$_id", "count": "$total_workouts"}}}},
    {"$unwind": "$user_counts"},
    {"$match": {"$expr": {"$gt": ["$user_counts.count", "$avg_count"]}}},
    {"$lookup": {"from": "users", "localField": "user_counts.user_id", "foreignField": "user_id", "as": "user"}},
    {"$unwind": "$user"},
    {"$project": {"name": "$user.name", "total_workouts": "$user_counts.count"}},
    {"$sort": {"total_workouts": -1}}
])
```

**Description:** Finds users who have completed more workouts than the average.

**SQL Equivalent:**
```sql
SELECT u.name, COUNT(*) AS total_workouts
FROM workouts w
JOIN users u ON w.user_id = u.user_id
GROUP BY u.user_id, u.name
HAVING total_workouts > (SELECT AVG(cnt) FROM (SELECT COUNT(*) AS cnt FROM workouts GROUP BY user_id) AS sub)
```

---

## 6. Set Operations (UNION) Queries

Queries using `$unionWith` to combine results from multiple collections, equivalent to SQL `UNION ALL`.

### Combined Tracking Data

```javascript
db.calorie_intake_logs.aggregate([
    {"$project": {"user_id": 1, "log_date": 1, "metric": {"$literal": "calories"}, "value": "$calories_consumed"}},
    {"$unionWith": {"coll": "sleep_duration_logs", "pipeline": [{"$project": {"user_id": 1, "log_date": "$log_date", "metric": {"$literal": "sleep"}, "value": "$sleep_duration_hours"}}]}},
    {"$sort": {"log_date": -1}},
    {"$limit": 100}
])
```

**Description:** Combines calorie intake and sleep duration logs into a unified view.

**SQL Equivalent:**
```sql
SELECT user_id, log_date, 'calories' AS metric, calories_consumed AS value
FROM calorie_intake_logs
UNION ALL
SELECT user_id, log_date, 'sleep', sleep_duration_hours
FROM sleep_duration_logs
ORDER BY log_date DESC
LIMIT 100
```

---

### Users with Goals OR Conditions

```javascript
db.users.aggregate([
    {"$lookup": {"from": "user_goals", "localField": "user_id", "foreignField": "user_id", "as": "goals"}},
    {"$lookup": {"from": "user_conditions", "localField": "user_id", "foreignField": "user_id", "as": "conditions"}},
    {"$match": {"$or": [{"goals": {"$ne": []}}, {"conditions": {"$ne": []}}]}},
    {"$project": {"user_id": 1, "name": 1, "has_goal": {"$cond": [{"$gt": [{"$size": "$goals"}, 0]}, "Yes", "No"]}, "has_condition": {"$cond": [{"$gt": [{"$size": "$conditions"}, 0]}, "Yes", "No"]}}},
    {"$limit": 50}
])
```

**Description:** Finds users who have set at least one goal OR have at least one medical condition.

---

## 7. Subqueries in Aggregation

Queries with multiple `$lookup` stages computing derived values, equivalent to SQL subqueries in `SELECT`.

### User Summary

```javascript
db.users.aggregate([
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
])
```

**Description:** Creates a summary view with workout count, goal count, and average weight as computed columns.

**SQL Equivalent:**
```sql
SELECT u.name, u.email,
    (SELECT COUNT(*) FROM workouts WHERE user_id = u.user_id) AS workout_count,
    (SELECT COUNT(*) FROM user_goals WHERE user_id = u.user_id) AS goal_count,
    (SELECT AVG(weight_kg) FROM weight_logs WHERE user_id = u.user_id) AS avg_weight
FROM users u
ORDER BY workout_count DESC
```

---

### Average Workouts Per User

```javascript
db.workouts.aggregate([
    {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
    {"$group": {"_id": null, "avg_workouts": {"$avg": "$count"}}},
    {"$project": {"avg_workouts_per_user": {"$round": ["$avg_workouts", 1]}}}
])
```

**Description:** Calculates the average number of workouts per user.

**SQL Equivalent:**
```sql
SELECT ROUND(AVG(workout_count), 1) AS avg_workouts_per_user
FROM (SELECT COUNT(*) AS workout_count FROM workouts GROUP BY user_id) AS sub
```

---

## Query Categories Summary

| Category | Query IDs | Description |
|:---------|:----------|:------------|
| Basic Find | N1-N4 | Simple queries on single collections |
| Aggregation | A1-A8 | GROUP BY with accumulators ($sum, $avg, $bucket) |
| Lookup (JOIN) | J1-J4 | $lookup to join collections |
| Outer Lookup | O1-O3 | $lookup + $size: 0 for missing data |
| Nested Aggregation | NS1-NS2 | Multi-stage complex pipelines |
| Set Operations | U1-U3 | $unionWith to combine collections |
| Subqueries | SM1-SM3 | Derived columns with $lookup |

---

## MongoDB Operator Reference

| Operator | Description | SQL Equivalent |
|:---------|:------------|:---------------|
| `$match` | Filter documents | WHERE |
| `$group` | Group documents | GROUP BY |
| `$project` | Shape/transform documents | SELECT (column selection) |
| `$sort` | Order documents | ORDER BY |
| `$limit` | Limit result count | LIMIT |
| `$lookup` | Join collections | JOIN |
| `$unwind` | Deconstruct arrays | (flattening) |
| `$bucket` | Create range groups | CASE WHEN / grouping |
| `$unionWith` | Combine collections | UNION ALL |
| `$sum` | Accumulator - sum | SUM() |
| `$avg` | Accumulator - average | AVG() |
| `$count` | Count documents | COUNT(*) |
| `$size` | Array length | (array check) |

---

*Generated from `utils/nosql_console.py`*
