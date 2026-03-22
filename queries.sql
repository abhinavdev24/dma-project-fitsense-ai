-- ============================================================
-- FitSense AI — Read Queries
-- ============================================================
USE fitsense_ai;

-- ============================================================
-- 1. BASIC COUNTS
-- ============================================================

-- Row counts for every table
SELECT 'users'                    AS tbl, COUNT(*) AS cnt FROM users
UNION ALL SELECT 'user_profiles',           COUNT(*) FROM user_profiles
UNION ALL SELECT 'user_goals',              COUNT(*) FROM user_goals
UNION ALL SELECT 'user_conditions',         COUNT(*) FROM user_conditions
UNION ALL SELECT 'user_allergies',          COUNT(*) FROM user_allergies
UNION ALL SELECT 'user_medications',        COUNT(*) FROM user_medications
UNION ALL SELECT 'user_medical_profiles',   COUNT(*) FROM user_medical_profiles
UNION ALL SELECT 'goals',                   COUNT(*) FROM goals
UNION ALL SELECT 'conditions',              COUNT(*) FROM conditions
UNION ALL SELECT 'equipment',               COUNT(*) FROM equipment
UNION ALL SELECT 'exercises',               COUNT(*) FROM exercises
UNION ALL SELECT 'workout_plans',           COUNT(*) FROM workout_plans
UNION ALL SELECT 'plan_days',               COUNT(*) FROM plan_days
UNION ALL SELECT 'plan_exercises',          COUNT(*) FROM plan_exercises
UNION ALL SELECT 'plan_sets',               COUNT(*) FROM plan_sets
UNION ALL SELECT 'workouts',                COUNT(*) FROM workouts
UNION ALL SELECT 'workout_exercises',       COUNT(*) FROM workout_exercises
UNION ALL SELECT 'workout_sets',            COUNT(*) FROM workout_sets
UNION ALL SELECT 'weight_logs',             COUNT(*) FROM weight_logs
UNION ALL SELECT 'sleep_duration_logs',     COUNT(*) FROM sleep_duration_logs
UNION ALL SELECT 'sleep_targets',           COUNT(*) FROM sleep_targets
UNION ALL SELECT 'calorie_intake_logs',     COUNT(*) FROM calorie_intake_logs
UNION ALL SELECT 'calorie_targets',         COUNT(*) FROM calorie_targets;


-- ============================================================
-- 2. USERS
-- ============================================================

-- All users, newest first
SELECT HEX(user_id) AS user_id, name, email, created_at
FROM users
ORDER BY created_at DESC;

-- Users created in the last 90 days
SELECT name, email, created_at
FROM users
WHERE created_at >= NOW() - INTERVAL 90 DAY;

-- Total users registered per month
SELECT DATE_FORMAT(created_at, '%Y-%m') AS month,
       COUNT(*) AS new_users
FROM users
GROUP BY month
ORDER BY month;

-- Search user by email (replace value)
SELECT HEX(user_id) AS user_id, name, email, created_at
FROM users
WHERE email = 'eden.jenkins.1@fitsense.synthetic';


-- ============================================================
-- 3. USER PROFILES
-- ============================================================

-- Age, sex, height and activity level per user
SELECT u.name,
       p.date_of_birth,
       TIMESTAMPDIFF(YEAR, p.date_of_birth, CURDATE()) AS age,
       p.sex,
       p.height_cm,
       p.activity_level
FROM users u
JOIN user_profiles p ON p.user_id = u.user_id
ORDER BY age DESC;

-- Breakdown by activity level
SELECT activity_level, COUNT(*) AS total
FROM user_profiles
GROUP BY activity_level
ORDER BY total DESC;

-- Breakdown by sex
SELECT sex, COUNT(*) AS total
FROM user_profiles
GROUP BY sex;

-- Average height by sex
SELECT sex,
       ROUND(AVG(height_cm), 1) AS avg_height_cm
FROM user_profiles
WHERE height_cm IS NOT NULL
GROUP BY sex;

-- Age distribution buckets
SELECT
    CASE
        WHEN TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) < 20 THEN 'Under 20'
        WHEN TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) < 30 THEN '20-29'
        WHEN TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) < 40 THEN '30-39'
        WHEN TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) < 50 THEN '40-49'
        ELSE '50+'
    END AS age_group,
    COUNT(*) AS total
FROM user_profiles
WHERE date_of_birth IS NOT NULL
GROUP BY age_group
ORDER BY age_group;

-- Users with complete profiles (all fields filled)
SELECT u.name, u.email
FROM users u
JOIN user_profiles p ON p.user_id = u.user_id
WHERE p.date_of_birth  IS NOT NULL
  AND p.sex            IS NOT NULL
  AND p.height_cm      IS NOT NULL
  AND p.activity_level IS NOT NULL;


-- ============================================================
-- 4. GOALS & CONDITIONS
-- ============================================================

-- Most popular goals
SELECT g.name, COUNT(*) AS total_users
FROM user_goals ug
JOIN goals g ON g.goal_id = ug.goal_id
GROUP BY g.name
ORDER BY total_users DESC;

-- Most common conditions
SELECT c.name, severity, COUNT(*) AS total
FROM user_conditions uc
JOIN conditions c ON c.condition_id = uc.condition_id
GROUP BY c.name, severity
ORDER BY total DESC;

-- Users with more than 1 goal
SELECT u.name, COUNT(*) AS goal_count
FROM user_goals ug
JOIN users u ON u.user_id = ug.user_id
GROUP BY u.name
HAVING goal_count > 1
ORDER BY goal_count DESC;

-- Users with no goals assigned
SELECT u.name, u.email
FROM users u
LEFT JOIN user_goals ug ON ug.user_id = u.user_id
WHERE ug.user_id IS NULL;

-- All goals for a specific user (replace email)
SELECT u.name, g.name AS goal, ug.priority
FROM user_goals ug
JOIN users u ON u.user_id = ug.user_id
JOIN goals g ON g.goal_id = ug.goal_id
WHERE u.email = 'eden.jenkins.1@fitsense.synthetic'
ORDER BY ug.priority;

-- Conditions breakdown by severity
SELECT severity, COUNT(*) AS total
FROM user_conditions
GROUP BY severity
ORDER BY total DESC;

-- Users with severe conditions
SELECT u.name, u.email, c.name AS condition
FROM user_conditions uc
JOIN users u ON u.user_id = uc.user_id
JOIN conditions c ON c.condition_id = uc.condition_id
WHERE uc.severity = 'severe'
ORDER BY u.name;


-- ============================================================
-- 5. MEDICAL PROFILES & MEDICATIONS
-- ============================================================

-- Users with injuries
SELECT u.name, m.injury_details
FROM user_medical_profiles m
JOIN users u ON u.user_id = m.user_id
WHERE m.has_injuries = 1;

-- Users currently on medication (no end date = still active)
SELECT u.name, um.medication_name, um.dosage, um.frequency, um.start_date
FROM user_medications um
JOIN users u ON u.user_id = um.user_id
WHERE um.end_date IS NULL
ORDER BY um.start_date DESC;

-- Most common medications
SELECT medication_name, COUNT(*) AS total_users
FROM user_medications
GROUP BY medication_name
ORDER BY total_users DESC;

-- Most common allergies
SELECT allergen, COUNT(*) AS total
FROM user_allergies
GROUP BY allergen
ORDER BY total DESC;

-- Severe allergies
SELECT u.name, a.allergen, a.reaction
FROM user_allergies a
JOIN users u ON u.user_id = a.user_id
WHERE a.severity = 'severe'
ORDER BY u.name;


-- ============================================================
-- 6. WORKOUTS
-- ============================================================

-- Most active users by workout count
SELECT u.name, COUNT(*) AS total_workouts
FROM workouts w
JOIN users u ON u.user_id = w.user_id
GROUP BY u.name
ORDER BY total_workouts DESC
LIMIT 10;

-- Average workout duration in minutes per user
SELECT u.name,
       ROUND(AVG(TIMESTAMPDIFF(MINUTE, w.started_at, w.ended_at)), 1) AS avg_duration_mins
FROM workouts w
JOIN users u ON u.user_id = w.user_id
WHERE w.started_at IS NOT NULL AND w.ended_at IS NOT NULL
GROUP BY u.name
ORDER BY avg_duration_mins DESC;

-- Workouts per month
SELECT DATE_FORMAT(started_at, '%Y-%m') AS month,
       COUNT(*) AS total_workouts
FROM workouts
WHERE started_at IS NOT NULL
GROUP BY month
ORDER BY month;

-- Workouts per day of week
SELECT DAYNAME(started_at) AS day_of_week,
       COUNT(*) AS total_workouts
FROM workouts
WHERE started_at IS NOT NULL
GROUP BY day_of_week, DAYOFWEEK(started_at)
ORDER BY DAYOFWEEK(started_at);

-- Longest workouts ever recorded
SELECT u.name,
       w.started_at,
       TIMESTAMPDIFF(MINUTE, w.started_at, w.ended_at) AS duration_mins
FROM workouts w
JOIN users u ON u.user_id = w.user_id
WHERE w.started_at IS NOT NULL AND w.ended_at IS NOT NULL
ORDER BY duration_mins DESC
LIMIT 10;

-- Workouts not linked to any plan (freeform)
SELECT u.name, w.started_at, w.notes
FROM workouts w
JOIN users u ON u.user_id = w.user_id
WHERE w.plan_id IS NULL
ORDER BY w.started_at DESC;

-- Total sets logged per user across all workouts
SELECT u.name, COUNT(ws.workout_set_id) AS total_sets
FROM workout_sets ws
JOIN workout_exercises we ON we.workout_exercise_id = ws.workout_exercise_id
JOIN workouts w           ON w.workout_id           = we.workout_id
JOIN users u              ON u.user_id              = w.user_id
GROUP BY u.name
ORDER BY total_sets DESC;

-- Average reps per set per user
SELECT u.name,
       ROUND(AVG(ws.reps), 1) AS avg_reps_per_set
FROM workout_sets ws
JOIN workout_exercises we ON we.workout_exercise_id = ws.workout_exercise_id
JOIN workouts w           ON w.workout_id           = we.workout_id
JOIN users u              ON u.user_id              = w.user_id
WHERE ws.reps IS NOT NULL
GROUP BY u.name
ORDER BY avg_reps_per_set DESC;


-- ============================================================
-- 7. EXERCISES & PLANS
-- ============================================================

-- Most used exercises across all workout plans
SELECT e.name, COUNT(*) AS times_programmed
FROM plan_exercises pe
JOIN exercises e ON e.exercise_id = pe.exercise_id
GROUP BY e.name
ORDER BY times_programmed DESC
LIMIT 10;

-- Exercises grouped by primary muscle
SELECT primary