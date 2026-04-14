# FitSense AI - SQL Queries Reference

This document provides examples of different SQL query types used in the FitSense AI Dashboard.

---

## 1. Simple Queries

Basic SELECT statements querying a single table.

```sql
SELECT 
    HEX(user_id) AS user_id, 
    name, 
    email, 
    created_at 
FROM users 
ORDER BY created_at DESC
```

**Description:** Retrieves all users with their basic information, ordered by creation date.

---

## 2. Aggregate Queries

Queries using GROUP BY with aggregation functions like COUNT, AVG, SUM.

```sql
SELECT 
    activity_level, 
    COUNT(*) AS total 
FROM user_profiles 
GROUP BY activity_level 
ORDER BY total DESC
```

**Description:** Counts users grouped by their activity level, sorted by total descending.

---

## 3. INNER JOIN Queries

Queries that combine data from multiple tables using INNER JOIN.

```sql
SELECT 
    u.name, 
    COUNT(*) AS total_workouts 
FROM workouts w 
JOIN users u ON u.user_id = w.user_id 
GROUP BY u.name 
ORDER BY total_workouts DESC 
LIMIT 10
```

**Description:** Finds the top 10 most active users based on workout count.

---

## 4. OUTER JOIN (LEFT JOIN) Queries

Queries using LEFT JOIN to find records with or without matches.

```sql
SELECT 
    u.name, 
    u.email 
FROM users u 
LEFT JOIN user_goals ug ON ug.user_id = u.user_id 
WHERE ug.user_id IS NULL
```

**Description:** Finds users who have not set any fitness goals.

---

## 5. Nested (Non-Correlated) Subqueries

Subqueries that are independent of the outer query and can run standalone.

```sql
SELECT 
    u.name, 
    COUNT(*) AS total_workouts 
FROM workouts w 
JOIN users u ON u.user_id = w.user_id 
GROUP BY u.name 
HAVING total_workouts > (
    SELECT AVG(cnt) 
    FROM (
        SELECT COUNT(*) AS cnt 
        FROM workouts 
        GROUP BY user_id
    ) AS sub
)
```

**Description:** Finds users who have more workouts than the average number of workouts per user.

---

## 6. Correlated Subqueries

Subqueries that reference columns from the outer query - they depend on the outer query to execute.

```sql
SELECT 
    u.name, 
    (
        SELECT COUNT(*) 
        FROM user_goals ug 
        WHERE ug.user_id = u.user_id
    ) AS goal_count 
FROM users u 
WHERE (
    SELECT COUNT(*) 
    FROM user_goals ug 
    WHERE ug.user_id = u.user_id
) > (
    SELECT AVG(gc) 
    FROM (
        SELECT COUNT(*) AS gc 
        FROM user_goals 
        GROUP BY user_id
    ) AS t
)
```

**Description:** Finds users who have more goals than the average number of goals across all users.

---

## 7. Set Operations (UNION / UNION ALL)

Queries that combine results from multiple SELECT statements.

```sql
SELECT 
    user_id, 
    log_date, 
    'calories' AS metric, 
    calories_consumed AS value 
FROM calorie_intake_logs 
UNION ALL SELECT 
    user_id, 
    log_date, 
    'sleep', 
    sleep_duration_hours 
FROM sleep_duration_logs
```

**Description:** Combines calorie intake and sleep duration logs into a unified tracking view.

---

## 8. Subqueries in SELECT Clause

Subqueries embedded within the SELECT statement to compute derived columns.

```sql
SELECT 
    u.name, 
    (
        SELECT COUNT(*) 
        FROM workouts w 
        WHERE w.user_id = u.user_id
    ) AS workout_count, 
    (
        SELECT COUNT(*) 
        FROM user_goals ug 
        WHERE ug.user_id = u.user_id
    ) AS goal_count, 
    (
        SELECT ROUND(AVG(wl.weight_kg), 1) 
        FROM weight_logs wl 
        WHERE wl.user_id = u.user_id
    ) AS avg_weight 
FROM users u 
ORDER BY workout_count DESC
```

**Description:** Creates a summary view with workout count, goal count, and average weight as computed columns.

---

## 9. Subqueries in FROM Clause

Subqueries used as derived tables within the FROM clause.

```sql
SELECT 
    sub.activity_level, 
    sub.total, 
    ROUND(sub.total * 100.0 / (
        SELECT COUNT(*) 
        FROM user_profiles
    ), 1) AS percentage 
FROM (
    SELECT activity_level, COUNT(*) AS total 
    FROM user_profiles 
    GROUP BY activity_level
) AS sub 
ORDER BY sub.total DESC
```

**Description:** Calculates the percentage of users at each activity level.

---

## 10. EXISTS / NOT EXISTS Queries

Queries using EXISTS and NOT EXISTS to check for record existence.

```sql
SELECT 
    u.name, 
    u.email 
FROM users u 
WHERE NOT EXISTS (
    SELECT 1 
    FROM sleep_duration_logs sdl 
    WHERE sdl.user_id = u.user_id
)
```

**Description:** Finds users who have never logged their sleep duration.

---

## 11. >= ALL / > ANY Queries

Queries using ALL and ANY modifiers for comparative operations.

```sql
SELECT 
    u.name, 
    COUNT(*) AS total 
FROM workouts w 
JOIN users u ON u.user_id = w.user_id 
GROUP BY u.user_id, u.name 
HAVING total >= ALL (
    SELECT COUNT(*) 
    FROM workouts 
    GROUP BY user_id
)
```

**Description:** Finds the user with the most workouts (the user whose count is >= all other counts).

---

## Query Categories Summary

| Category | Query IDs | Description |
|----------|-----------|-------------|
| Simple | S1-S4 | Basic single-table queries |
| Aggregate | A1-A8 | GROUP BY with aggregation |
| INNER JOIN | J1-J4 | Table joins with matching records |
| OUTER JOIN | O1-O3 | LEFT JOIN for missing records |
| Nested Subquery | N1-N2 | Independent subqueries |
| Correlated Subquery | C1-C2 | Subqueries referencing outer query |
| Set Operations | U1-U3 | UNION/UNION ALL combinations |
| Subquery in SELECT | SS1 | Derived columns |
| Subquery in FROM | SF1-SF2 | Derived tables |
| EXISTS/NOT EXISTS | E3-E4 | Record existence checks |
| ALL/ANY | E1-E2 | Comparative operators |

---

*Generated from `utils/queries.py`*
