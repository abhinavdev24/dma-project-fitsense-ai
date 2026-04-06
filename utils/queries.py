"""
SQL Queries for FitSense AI Dashboard
All SQL queries organized by category and SQL concept coverage.
"""

# =============================================================================
# SIMPLE QUERIES
# =============================================================================

S1_ALL_USERS = """
    SELECT 
        HEX(user_id) AS user_id, 
        name, 
        email, 
        created_at 
    FROM users 
    ORDER BY created_at DESC
"""

S2_ALL_EXERCISES = """
    SELECT 
        HEX(exercise_id) AS id, 
        name, 
        primary_muscle 
    FROM exercises 
    ORDER BY name
"""

S3_ALL_GOALS = """
    SELECT 
        HEX(goal_id) AS id, 
        name, 
        description 
    FROM goals
"""

S4_RECENT_WORKOUTS = """
    SELECT 
        HEX(w.workout_id) AS id, 
        w.started_at, 
        w.ended_at, 
        w.notes 
    FROM workouts w 
    WHERE w.started_at >= NOW() - INTERVAL 30 DAY 
    ORDER BY w.started_at DESC
"""

# =============================================================================
# AGGREGATE QUERIES
# =============================================================================

A1_USERS_BY_ACTIVITY_LEVEL = """
    SELECT 
        activity_level, 
        COUNT(*) AS total 
    FROM user_profiles 
    GROUP BY activity_level 
    ORDER BY total DESC
"""

A2_USERS_BY_SEX = """
    SELECT 
        sex, 
        COUNT(*) AS total 
    FROM user_profiles 
    GROUP BY sex
"""

A3_AVG_HEIGHT_BY_SEX = """
    SELECT 
        sex, 
        ROUND(AVG(height_cm), 1) AS avg_height 
    FROM user_profiles 
    WHERE height_cm IS NOT NULL 
    GROUP BY sex
"""

A4_AGE_DISTRIBUTION = """
    SELECT 
        CASE 
            WHEN TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) < 20 THEN 'Under 20'
            WHEN TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) BETWEEN 20 AND 29 THEN '20-29'
            WHEN TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) BETWEEN 30 AND 39 THEN '30-39'
            WHEN TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) BETWEEN 40 AND 49 THEN '40-49'
            WHEN TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) BETWEEN 50 AND 59 THEN '50-59'
            ELSE '60+'
        END AS age_group, 
        COUNT(*) AS total 
    FROM user_profiles 
    WHERE date_of_birth IS NOT NULL 
    GROUP BY age_group
"""

A5_WORKOUTS_PER_DAY = """
    SELECT 
        DAYNAME(started_at) AS day_of_week, 
        COUNT(*) AS total 
    FROM workouts 
    WHERE started_at IS NOT NULL 
    GROUP BY day_of_week, DAYOFWEEK(started_at) 
    ORDER BY DAYOFWEEK(started_at)
"""

A6_MOST_POPULAR_GOALS = """
    SELECT 
        g.name, 
        COUNT(*) AS total_users 
    FROM user_goals ug 
    JOIN goals g ON g.goal_id = ug.goal_id 
    GROUP BY g.name 
    ORDER BY total_users DESC
"""

A7_CONDITIONS_BY_SEVERITY = """
    SELECT 
        severity, 
        COUNT(*) AS total 
    FROM user_conditions 
    GROUP BY severity 
    ORDER BY total DESC
"""

A8_AVG_WORKOUT_DURATION = """
    SELECT 
        u.name, 
        ROUND(AVG(TIMESTAMPDIFF(MINUTE, w.started_at, w.ended_at)), 1) AS avg_mins 
    FROM workouts w 
    JOIN users u ON u.user_id = w.user_id 
    WHERE w.started_at IS NOT NULL 
    AND w.ended_at IS NOT NULL 
    GROUP BY u.name 
    ORDER BY avg_mins DESC
"""

# =============================================================================
# INNER JOIN QUERIES
# =============================================================================

J1_USER_PROFILES_DEMOGRAPHICS = """
    SELECT 
        u.name, 
        p.date_of_birth, 
        TIMESTAMPDIFF(YEAR, p.date_of_birth, CURDATE()) AS age, 
        p.sex, 
        p.height_cm, 
        p.activity_level 
    FROM users u 
    JOIN user_profiles p ON p.user_id = u.user_id 
    ORDER BY age DESC
"""

J2_MOST_USED_EXERCISES = """
    SELECT 
        e.name, 
        COUNT(*) AS times_programmed 
    FROM plan_exercises pe 
    JOIN exercises e ON e.exercise_id = pe.exercise_id 
    GROUP BY e.name 
    ORDER BY times_programmed DESC 
    LIMIT 10
"""

J3_TOP_ACTIVE_USERS = """
    SELECT 
        u.name, 
        COUNT(*) AS total_workouts 
    FROM workouts w 
    JOIN users u ON u.user_id = w.user_id 
    GROUP BY u.name 
    ORDER BY total_workouts DESC 
    LIMIT 10
"""

J4_USERS_WITH_SEVERE_CONDITIONS = """
    SELECT 
        u.name, 
        u.email, 
        c.name AS condition_name 
    FROM user_conditions uc 
    JOIN users u ON u.user_id = uc.user_id 
    JOIN conditions c ON c.condition_id = uc.condition_id 
    WHERE uc.severity = 'severe' 
    ORDER BY u.name
"""

# =============================================================================
# OUTER JOIN QUERIES (LEFT JOIN)
# =============================================================================

O1_USERS_WITH_NO_GOALS = """
    SELECT 
        u.name, 
        u.email 
    FROM users u 
    LEFT JOIN user_goals ug ON ug.user_id = u.user_id 
    WHERE ug.user_id IS NULL
"""

O2_USERS_WITH_NO_WORKOUTS = """
    SELECT 
        u.name, 
        u.email 
    FROM users u 
    LEFT JOIN workouts w ON w.user_id = u.user_id 
    WHERE w.workout_id IS NULL
"""

O3_EXERCISES_NEVER_USED = """
    SELECT 
        e.name, 
        e.primary_muscle 
    FROM exercises e 
    LEFT JOIN plan_exercises pe ON pe.exercise_id = e.exercise_id 
    WHERE pe.plan_exercise_id IS NULL
"""

# =============================================================================
# NESTED (NON-CORRELATED) SUBQUERIES
# =============================================================================

N1_USERS_ABOVE_AVERAGE_WORKOUTS = """
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
"""

N2_HEAVIEST_LIFTS_ABOVE_AVG = """
    SELECT 
        HEX(ws.workout_set_id) AS id,
        ws.weight, 
        ws.reps 
    FROM workout_sets ws 
    WHERE ws.weight > (
        SELECT AVG(weight) 
        FROM workout_sets 
        WHERE weight IS NOT NULL
    )
"""

# =============================================================================
# CORRELATED SUBQUERIES
# =============================================================================

C1_USERS_LAST_WORKOUT_EXCEEDED_AVG = """
    SELECT 
        u.name, 
        TIMESTAMPDIFF(MINUTE, w.started_at, w.ended_at) AS last_duration 
    FROM workouts w 
    JOIN users u ON u.user_id = w.user_id 
    WHERE w.started_at = (
        SELECT MAX(w2.started_at) 
        FROM workouts w2 
        WHERE w2.user_id = w.user_id
    ) 
    AND TIMESTAMPDIFF(MINUTE, w.started_at, w.ended_at) > (
        SELECT AVG(TIMESTAMPDIFF(MINUTE, w3.started_at, w3.ended_at)) 
        FROM workouts w3 
        WHERE w3.user_id = w.user_id 
        AND w3.started_at IS NOT NULL 
        AND w3.ended_at IS NOT NULL
    )
"""

C2_USERS_WITH_MORE_GOALS_THAN_AVG = """
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
"""

# =============================================================================
# >= ALL / > ANY / EXISTS / NOT EXISTS
# =============================================================================

E1_USER_WITH_MOST_WORKOUTS = """
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
"""

E2_USERS_SLEEPING_MORE_THAN_ANY_TARGET = """
    SELECT DISTINCT 
        u.name 
    FROM users u 
    JOIN sleep_duration_logs sdl ON sdl.user_id = u.user_id 
    WHERE sdl.sleep_duration_hours > ANY (
        SELECT st.target_sleep_hours 
        FROM sleep_targets st 
        WHERE st.user_id = u.user_id
    )
"""

E3_USERS_WHO_LOGGED_WEIGHT = """
    SELECT 
        u.name, 
        u.email 
    FROM users u 
    WHERE EXISTS (
        SELECT 1 
        FROM weight_logs wl 
        WHERE wl.user_id = u.user_id
    )
"""

E4_USERS_WHO_NEVER_LOGGED_SLEEP = """
    SELECT 
        u.name, 
        u.email 
    FROM users u 
    WHERE NOT EXISTS (
        SELECT 1 
        FROM sleep_duration_logs sdl 
        WHERE sdl.user_id = u.user_id
    )
"""

# =============================================================================
# SET OPERATIONS (UNION)
# =============================================================================

U1_TABLE_ROW_COUNTS = """
    SELECT 'users' AS tbl, COUNT(*) AS cnt FROM users
    UNION ALL SELECT 'user_profiles', COUNT(*) FROM user_profiles
    UNION ALL SELECT 'goals', COUNT(*) FROM goals
    UNION ALL SELECT 'user_goals', COUNT(*) FROM user_goals
    UNION ALL SELECT 'conditions', COUNT(*) FROM conditions
    UNION ALL SELECT 'user_conditions', COUNT(*) FROM user_conditions
    UNION ALL SELECT 'equipment', COUNT(*) FROM equipment
    UNION ALL SELECT 'exercises', COUNT(*) FROM exercises
    UNION ALL SELECT 'exercise_equipment', COUNT(*) FROM exercise_equipment
    UNION ALL SELECT 'workout_plans', COUNT(*) FROM workout_plans
    UNION ALL SELECT 'plan_days', COUNT(*) FROM plan_days
    UNION ALL SELECT 'plan_exercises', COUNT(*) FROM plan_exercises
    UNION ALL SELECT 'plan_sets', COUNT(*) FROM plan_sets
    UNION ALL SELECT 'workouts', COUNT(*) FROM workouts
    UNION ALL SELECT 'workout_exercises', COUNT(*) FROM workout_exercises
    UNION ALL SELECT 'workout_sets', COUNT(*) FROM workout_sets
    UNION ALL SELECT 'weight_logs', COUNT(*) FROM weight_logs
    UNION ALL SELECT 'sleep_targets', COUNT(*) FROM sleep_targets
    UNION ALL SELECT 'sleep_duration_logs', COUNT(*) FROM sleep_duration_logs
    UNION ALL SELECT 'calorie_targets', COUNT(*) FROM calorie_targets
    UNION ALL SELECT 'calorie_intake_logs', COUNT(*) FROM calorie_intake_logs
    UNION ALL SELECT 'ai_interactions', COUNT(*) FROM ai_interactions
"""

U2_USERS_WITH_GOALS_OR_CONDITIONS = """
    SELECT 
        HEX(u.user_id) AS id, 
        u.name, 
        'Has Goal' AS attribute 
    FROM users u 
    JOIN user_goals ug ON ug.user_id = u.user_id 
    UNION SELECT 
        HEX(u.user_id), 
        u.name, 
        'Has Condition' 
    FROM users u 
    JOIN user_conditions uc ON uc.user_id = u.user_id
"""

U3_COMBINED_TRACKING_DATA = """
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
"""

# =============================================================================
# SUBQUERIES IN SELECT AND FROM
# =============================================================================

SS1_USER_SUMMARY = """
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
"""

SF1_AVG_WORKOUTS_PER_USER = """
    SELECT 
        ROUND(AVG(sub.total_workouts), 1) AS avg_workouts_per_user 
    FROM (
        SELECT user_id, COUNT(*) AS total_workouts 
        FROM workouts 
        GROUP BY user_id
    ) AS sub
"""

SF2_ACTIVITY_LEVEL_WITH_PERCENTAGE = """
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
"""

# =============================================================================
# ADDITIONAL CUSTOM QUERIES FOR SPECIFIC PAGES
# =============================================================================

# Weight page queries
WEIGHT_VS_BODY_FAT = """
    SELECT 
        wl.weight_kg, 
        wl.body_fat_percentage, 
        wl.logged_at 
    FROM weight_logs wl 
    WHERE wl.weight_kg IS NOT NULL 
    AND wl.body_fat_percentage IS NOT NULL
"""

WEIGHT_TREND = """
    SELECT 
        wl.user_id,
        wl.logged_at, 
        wl.weight_kg 
    FROM weight_logs wl 
    WHERE wl.weight_kg IS NOT NULL 
    ORDER BY wl.logged_at
"""

WEIGHT_DISTRIBUTION_BY_SEX = """
    SELECT 
        p.sex, 
        wl.weight_kg 
    FROM weight_logs wl 
    JOIN user_profiles p ON p.user_id = wl.user_id 
    WHERE wl.weight_kg IS NOT NULL 
    AND p.sex IS NOT NULL
"""

# Sleep page queries
SLEEP_DURATION_BY_ACTIVITY = """
    SELECT 
        p.activity_level, 
        sdl.sleep_duration_hours 
    FROM sleep_duration_logs sdl 
    JOIN user_profiles p ON p.user_id = sdl.user_id 
    WHERE p.activity_level IS NOT NULL 
    AND sdl.sleep_duration_hours IS NOT NULL
"""

SLEEP_DURATION_TREND = """
    SELECT 
        sdl.log_date, 
        AVG(sdl.sleep_duration_hours) AS avg_sleep_hours 
    FROM sleep_duration_logs sdl 
    WHERE sdl.sleep_duration_hours IS NOT NULL 
    GROUP BY sdl.log_date 
    ORDER BY sdl.log_date
"""

# Nutrition page queries
CALORIE_INTAKE_TREND = """
    SELECT 
        cil.log_date, 
        AVG(cil.calories_consumed) AS avg_calories 
    FROM calorie_intake_logs cil 
    WHERE cil.calories_consumed IS NOT NULL 
    GROUP BY cil.log_date 
    ORDER BY cil.log_date
"""

CALORIES_VS_TARGET = """
    SELECT 
        cil.user_id,
        cil.log_date, 
        cil.calories_consumed, 
        ct.maintenance_calories AS target 
    FROM calorie_intake_logs cil 
    JOIN calorie_targets ct ON ct.user_id = cil.user_id 
    WHERE cil.calories_consumed IS NOT NULL 
    ORDER BY cil.log_date
"""

# =============================================================================
# APP PAGE QUERIES (Quick Stats)
# =============================================================================

APP_COUNT_USERS = """
    SELECT COUNT(*) as cnt FROM users
"""

APP_COUNT_WORKOUTS = """
    SELECT COUNT(*) as cnt FROM workouts
"""

APP_AVG_SLEEP_DURATION = """
    SELECT ROUND(AVG(sleep_duration_hours), 1) as avg FROM sleep_duration_logs
"""

APP_COUNT_ACTIVE_PLANS = """
    SELECT COUNT(*) as cnt FROM workout_plans WHERE is_active = 1
"""

# =============================================================================
# NUTRITION PAGE QUERIES
# =============================================================================

NUTRITION_TOTAL_LOGS = """
    SELECT COUNT(*) as total_logs FROM calorie_intake_logs
"""

NUTRITION_AVG_CALORIES = """
    SELECT ROUND(AVG(calories_consumed), 0) as avg_calories FROM calorie_intake_logs
"""

NUTRITION_USERS_TRACKING = """
    SELECT COUNT(DISTINCT user_id) as users_tracking FROM calorie_intake_logs
"""

NUTRITION_USERS_WITH_TARGETS = """
    SELECT COUNT(DISTINCT user_id) as users_with_targets FROM calorie_targets
"""

NUTRITION_INTAKE_TREND_30D = """
    SELECT 
        log_date,
        ROUND(AVG(calories_consumed), 0) as avg_calories,
        COUNT(*) as log_count
    FROM calorie_intake_logs
    WHERE log_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
    GROUP BY log_date
    ORDER BY log_date
"""

NUTRITION_TOP_USERS_TOTAL = """
    SELECT 
        u.name,
        SUM(cil.calories_consumed) as total_calories,
        COUNT(*) as log_count
    FROM calorie_intake_logs cil
    JOIN users u ON cil.user_id = u.user_id
    GROUP BY u.user_id, u.name
    ORDER BY total_calories DESC
    LIMIT 10
"""

NUTRITION_TOP_USERS_AVG = """
    SELECT 
        u.name,
        ROUND(AVG(cil.calories_consumed), 0) as avg_calories,
        COUNT(*) as log_count
    FROM calorie_intake_logs cil
    JOIN users u ON cil.user_id = u.user_id
    GROUP BY u.user_id, u.name
    HAVING log_count >= 10
    ORDER BY avg_calories DESC
    LIMIT 10
"""

NUTRITION_BY_DAY_OF_WEEK = """
    SELECT 
        DAYNAME(log_date) as day_name,
        DAYOFWEEK(log_date) as day_num,
        ROUND(AVG(calories_consumed), 0) as avg_calories,
        COUNT(*) as log_count
    FROM calorie_intake_logs
    WHERE log_date IS NOT NULL
    GROUP BY DAYNAME(log_date), DAYOFWEEK(log_date)
    ORDER BY day_num
"""

NUTRITION_DISTRIBUTION = """
    SELECT 
        calories_consumed
    FROM calorie_intake_logs
    WHERE calories_consumed IS NOT NULL
"""

NUTRITION_RECENT_LOGS = """
    SELECT 
        u.name as user_name,
        cil.log_date,
        cil.calories_consumed
    FROM calorie_intake_logs cil
    JOIN users u ON cil.user_id = u.user_id
    ORDER BY cil.log_date DESC, cil.calories_consumed DESC
    LIMIT 50
"""

NUTRITION_USER_TARGETS = """
    SELECT 
        u.name as user_name,
        ct.maintenance_calories,
        ct.method
    FROM calorie_targets ct
    JOIN users u ON ct.user_id = u.user_id
    ORDER BY u.name
    LIMIT 30
"""

# =============================================================================
# SLEEP PAGE QUERIES
# =============================================================================

SLEEP_TOTAL_LOGS = """
    SELECT COUNT(*) as total_logs FROM sleep_duration_logs
"""

SLEEP_AVG_DURATION = """
    SELECT ROUND(AVG(sleep_duration_hours), 1) as avg_hours FROM sleep_duration_logs
"""

SLEEP_USERS_TRACKING = """
    SELECT COUNT(DISTINCT user_id) as users_tracking FROM sleep_duration_logs
"""

SLEEP_USERS_WITH_TARGETS = """
    SELECT COUNT(DISTINCT user_id) as users_with_targets FROM sleep_targets
"""

SLEEP_DURATION_TREND_AGG = """
    SELECT 
        log_date,
        ROUND(AVG(sleep_duration_hours), 2) as avg_sleep_hours,
        COUNT(*) as log_count
    FROM sleep_duration_logs
    GROUP BY log_date
    ORDER BY log_date
"""

SLEEP_BY_ACTIVITY_LEVEL = """
    SELECT 
        p.activity_level,
        sdl.sleep_duration_hours
    FROM sleep_duration_logs sdl
    JOIN user_profiles p ON p.user_id = sdl.user_id
    WHERE p.activity_level IS NOT NULL
    AND sdl.sleep_duration_hours IS NOT NULL
"""

SLEEP_BY_DAY_OF_WEEK = """
    SELECT 
        DAYNAME(log_date) as day_name,
        DAYOFWEEK(log_date) as day_num,
        ROUND(AVG(sleep_duration_hours), 2) as avg_hours,
        COUNT(*) as log_count
    FROM sleep_duration_logs
    WHERE log_date IS NOT NULL
    GROUP BY DAYNAME(log_date), DAYOFWEEK(log_date)
    ORDER BY day_num
"""

SLEEP_USERS_EXCEEDING_TARGET = """
    SELECT DISTINCT
        u.name,
        sdl.sleep_duration_hours,
        st.target_sleep_hours
    FROM users u
    JOIN sleep_duration_logs sdl ON sdl.user_id = u.user_id
    JOIN sleep_targets st ON st.user_id = u.user_id
    WHERE sdl.sleep_duration_hours > ANY (
        SELECT st2.target_sleep_hours
        FROM sleep_targets st2
        WHERE st2.user_id = u.user_id
    )
    LIMIT 20
"""

SLEEP_USERS_NEVER_LOGGED = """
    SELECT 
        u.name,
        u.email
    FROM users u
    WHERE NOT EXISTS (
        SELECT 1 
        FROM sleep_duration_logs sdl 
        WHERE sdl.user_id = u.user_id
    )
    LIMIT 20
"""

SLEEP_RECENT_LOGS = """
    SELECT 
        u.name as user_name,
        sdl.log_date,
        sdl.sleep_duration_hours
    FROM sleep_duration_logs sdl
    JOIN users u ON sdl.user_id = u.user_id
    ORDER BY sdl.log_date DESC
    LIMIT 50
"""

# =============================================================================
# WEIGHT PAGE QUERIES
# =============================================================================

WEIGHT_TOTAL_LOGS = """
    SELECT COUNT(*) as total_weight_logs FROM weight_logs
"""

WEIGHT_AVG_WEIGHT = """
    SELECT ROUND(AVG(weight_kg), 1) as avg_weight FROM weight_logs WHERE weight_kg IS NOT NULL
"""

WEIGHT_AVG_BODY_FAT = """
    SELECT ROUND(AVG(body_fat_percentage), 1) as avg_body_fat FROM weight_logs WHERE body_fat_percentage IS NOT NULL
"""

WEIGHT_USERS_TRACKING = """
    SELECT COUNT(DISTINCT user_id) as users_tracking_weight FROM weight_logs
"""

WEIGHT_VS_BODY_FAT_JOINED = """
    SELECT
        u.user_id,
        u.name as username,
        w.weight_kg as weight,
        w.body_fat_percentage,
        up.activity_level
    FROM weight_logs w
    JOIN users u ON w.user_id = u.user_id
    JOIN user_profiles up ON u.user_id = up.user_id
    WHERE w.weight_kg IS NOT NULL
    AND w.body_fat_percentage IS NOT NULL
    ORDER BY w.logged_at DESC
"""

WEIGHT_DISTRIBUTION_BY_SEX_JOINED = """
    SELECT
        up.sex,
        w.weight_kg as weight
    FROM weight_logs w
    JOIN users u ON w.user_id = u.user_id
    JOIN user_profiles up ON u.user_id = up.user_id
    WHERE w.weight_kg IS NOT NULL
    AND up.sex IS NOT NULL
"""

WEIGHT_TREND_90D = """
    SELECT
        DATE(w.logged_at) as date,
        ROUND(AVG(w.weight_kg), 2) as avg_weight,
        COUNT(*) as log_count
    FROM weight_logs w
    WHERE w.logged_at >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
    GROUP BY DATE(w.logged_at)
    ORDER BY date
"""

WEIGHT_BY_ACTIVITY_LEVEL = """
    SELECT
        up.activity_level,
        ROUND(AVG(w.weight_kg), 2) as avg_weight,
        ROUND(AVG(w.body_fat_percentage), 2) as avg_body_fat,
        COUNT(*) as user_count
    FROM weight_logs w
    JOIN users u ON w.user_id = u.user_id
    JOIN user_profiles up ON u.user_id = up.user_id
    WHERE w.weight_kg IS NOT NULL
    GROUP BY up.activity_level
    ORDER BY avg_weight DESC
"""

WEIGHT_BODY_FAT_RANGES = """
    SELECT
        CASE
            WHEN body_fat_percentage < 10 THEN '1-<10%'
            WHEN body_fat_percentage < 15 THEN '2-10-15%'
            WHEN body_fat_percentage < 20 THEN '3-15-20%'
            WHEN body_fat_percentage < 25 THEN '4-20-25%'
            WHEN body_fat_percentage < 30 THEN '5-25-30%'
            ELSE '6-30%+'
        END as body_fat_range,
        COUNT(*) as count
    FROM weight_logs
    WHERE body_fat_percentage IS NOT NULL
    GROUP BY body_fat_range
    ORDER BY body_fat_range
"""

WEIGHT_USERS_WITH_GOALS = """
    SELECT
        u.user_id,
        u.name as username,
        g.name as goal_name,
        ug.priority,
        w.weight_kg as current_weight
    FROM user_goals ug
    JOIN users u ON ug.user_id = u.user_id
    JOIN goals g ON ug.goal_id = g.goal_id
    JOIN weight_logs w ON u.user_id = w.user_id
    WHERE g.name LIKE '%weight%'
    AND w.logged_at = (
        SELECT MAX(logged_at) FROM weight_logs WHERE user_id = u.user_id
    )
    ORDER BY ug.priority ASC, u.name
    LIMIT 20
"""

# Query metadata for the SQL Console
QUERY_METADATA = {
    'S1': {'name': 'All Users', 'type': 'Simple Query', 'page': 'Users'},
    'S2': {'name': 'All Exercises', 'type': 'Simple Query', 'page': 'Workouts'},
    'S3': {'name': 'All Goals', 'type': 'Simple Query', 'page': 'Overview'},
    'S4': {'name': 'Recent Workouts', 'type': 'Simple Query', 'page': 'Overview'},
    'A1': {'name': 'Users by Activity Level', 'type': 'Aggregate', 'page': 'Users'},
    'A2': {'name': 'Users by Sex', 'type': 'Aggregate', 'page': 'Users'},
    'A3': {'name': 'Avg Height by Sex', 'type': 'Aggregate', 'page': 'Users'},
    'A4': {'name': 'Age Distribution', 'type': 'Aggregate', 'page': 'Users'},
    'A5': {'name': 'Workouts per Day of Week', 'type': 'Aggregate', 'page': 'Workouts'},
    'A6': {'name': 'Most Popular Goals', 'type': 'Aggregate + Join', 'page': 'Overview'},
    'A7': {'name': 'Conditions by Severity', 'type': 'Aggregate', 'page': 'Overview'},
    'A8': {'name': 'Avg Workout Duration', 'type': 'Aggregate + Join', 'page': 'Workouts'},
    'J1': {'name': 'User Demographics', 'type': 'INNER JOIN', 'page': 'Users'},
    'J2': {'name': 'Most Used Exercises', 'type': 'INNER JOIN', 'page': 'Workouts'},
    'J3': {'name': 'Top Active Users', 'type': 'INNER JOIN', 'page': 'Overview'},
    'J4': {'name': 'Users with Severe Conditions', 'type': 'INNER JOIN', 'page': 'Users'},
    'O1': {'name': 'Users with No Goals', 'type': 'LEFT JOIN', 'page': 'Overview'},
    'O2': {'name': 'Users with No Workouts', 'type': 'LEFT JOIN', 'page': 'Overview'},
    'O3': {'name': 'Exercises Never Used', 'type': 'LEFT JOIN', 'page': 'Workouts'},
    'N1': {'name': 'Users Above Avg Workouts', 'type': 'Nested Subquery', 'page': 'Workouts'},
    'N2': {'name': 'Heaviest Lifts Above Avg', 'type': 'Nested Subquery', 'page': 'Workouts'},
    'C1': {'name': 'Last Workout > Avg Duration', 'type': 'Correlated Subquery', 'page': 'Workouts'},
    'C2': {'name': 'Users with More Goals Than Avg', 'type': 'Correlated Subquery', 'page': 'Users'},
    'E1': {'name': 'User with Most Workouts', 'type': '>= ALL', 'page': 'Workouts'},
    'E2': {'name': 'Users Exceeding Sleep Target', 'type': '> ANY', 'page': 'Sleep'},
    'E3': {'name': 'Users Who Logged Weight', 'type': 'EXISTS', 'page': 'Overview'},
    'E4': {'name': 'Users Who Never Logged Sleep', 'type': 'NOT EXISTS', 'page': 'Sleep'},
    'U1': {'name': 'Table Row Counts', 'type': 'UNION ALL', 'page': 'Overview'},
    'U2': {'name': 'Users with Goals OR Conditions', 'type': 'UNION', 'page': 'Users'},
    'U3': {'name': 'Combined Tracking Data', 'type': 'UNION ALL', 'page': 'Nutrition'},
    'SS1': {'name': 'User Summary', 'type': 'Subquery in SELECT', 'page': 'Overview'},
    'SF1': {'name': 'Avg Workouts Per User', 'type': 'Subquery in FROM', 'page': 'Overview'},
    'SF2': {'name': 'Activity Level with %', 'type': 'Subquery in FROM', 'page': 'Users'},
}

# =============================================================================
# QUERY CATEGORIES FOR SQL EXPLORER
# =============================================================================

QUERY_CATEGORIES = {
    'Simple Queries': ['S1', 'S2', 'S3', 'S4'],
    'Aggregate Queries': ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8'],
    'INNER JOIN Queries': ['J1', 'J2', 'J3', 'J4'],
    'OUTER JOIN Queries': ['O1', 'O2', 'O3'],
    'Nested Subqueries': ['N1', 'N2'],
    'Correlated Subqueries': ['C1', 'C2'],
    'Set Operations': ['E1', 'E2', 'E3', 'E4', 'U1', 'U2', 'U3'],
    'Subqueries in SELECT/FROM': ['SS1', 'SF1', 'SF2'],
}

# =============================================================================
# QUERY LOOKUP DICTIONARY
# =============================================================================

QUERIES = {
    # Simple Queries
    'S1': S1_ALL_USERS,
    'S2': S2_ALL_EXERCISES,
    'S3': S3_ALL_GOALS,
    'S4': S4_RECENT_WORKOUTS,
    # Aggregate Queries
    'A1': A1_USERS_BY_ACTIVITY_LEVEL,
    'A2': A1_USERS_BY_ACTIVITY_LEVEL,  # Will be overridden
    'A3': A3_AVG_HEIGHT_BY_SEX,
    'A4': A4_AGE_DISTRIBUTION,
    'A5': A5_WORKOUTS_PER_DAY,
    'A6': A6_MOST_POPULAR_GOALS,
    'A7': A7_CONDITIONS_BY_SEVERITY,
    'A8': A8_AVG_WORKOUT_DURATION,
    # INNER JOIN Queries
    'J1': J1_USER_PROFILES_DEMOGRAPHICS,
    'J2': J2_MOST_USED_EXERCISES,
    'J3': J3_TOP_ACTIVE_USERS,
    'J4': J4_USERS_WITH_SEVERE_CONDITIONS,
    # OUTER JOIN Queries
    'O1': O1_USERS_WITH_NO_GOALS,
    'O2': O2_USERS_WITH_NO_WORKOUTS,
    'O3': O3_EXERCISES_NEVER_USED,
    # Nested Subqueries
    'N1': N1_USERS_ABOVE_AVERAGE_WORKOUTS,
    'N2': N2_HEAVIEST_LIFTS_ABOVE_AVG,
    # Correlated Subqueries
    'C1': C1_USERS_LAST_WORKOUT_EXCEEDED_AVG,
    'C2': C2_USERS_WITH_MORE_GOALS_THAN_AVG,
    # Set Operations
    'E1': E1_USER_WITH_MOST_WORKOUTS,
    'E2': E2_USERS_SLEEPING_MORE_THAN_ANY_TARGET,
    'E3': E3_USERS_WHO_LOGGED_WEIGHT,
    'E4': E4_USERS_WHO_NEVER_LOGGED_SLEEP,
    'U1': U1_TABLE_ROW_COUNTS,
    'U2': U2_USERS_WITH_GOALS_OR_CONDITIONS,
    'U3': U3_COMBINED_TRACKING_DATA,
    # Subqueries in SELECT/FROM
    'SS1': SS1_USER_SUMMARY,
    'SF1': SF1_AVG_WORKOUTS_PER_USER,
    'SF2': SF2_ACTIVITY_LEVEL_WITH_PERCENTAGE,
    # Additional Custom Queries
    'WEIGHT_VS_BODY_FAT': WEIGHT_VS_BODY_FAT,
    'WEIGHT_TREND': WEIGHT_TREND,
    'WEIGHT_DISTRIBUTION_BY_SEX': WEIGHT_DISTRIBUTION_BY_SEX,
    'SLEEP_DURATION_BY_ACTIVITY': SLEEP_DURATION_BY_ACTIVITY,
    'SLEEP_DURATION_TREND': SLEEP_DURATION_TREND,
    'CALORIE_INTAKE_TREND': CALORIE_INTAKE_TREND,
    'CALORIES_VS_TARGET': CALORIES_VS_TARGET,
    # App page queries
    'APP_COUNT_USERS': APP_COUNT_USERS,
    'APP_COUNT_WORKOUTS': APP_COUNT_WORKOUTS,
    'APP_AVG_SLEEP_DURATION': APP_AVG_SLEEP_DURATION,
    'APP_COUNT_ACTIVE_PLANS': APP_COUNT_ACTIVE_PLANS,
    # Nutrition page queries
    'NUTRITION_TOTAL_LOGS': NUTRITION_TOTAL_LOGS,
    'NUTRITION_AVG_CALORIES': NUTRITION_AVG_CALORIES,
    'NUTRITION_USERS_TRACKING': NUTRITION_USERS_TRACKING,
    'NUTRITION_USERS_WITH_TARGETS': NUTRITION_USERS_WITH_TARGETS,
    'NUTRITION_INTAKE_TREND_30D': NUTRITION_INTAKE_TREND_30D,
    'NUTRITION_TOP_USERS_TOTAL': NUTRITION_TOP_USERS_TOTAL,
    'NUTRITION_TOP_USERS_AVG': NUTRITION_TOP_USERS_AVG,
    'NUTRITION_BY_DAY_OF_WEEK': NUTRITION_BY_DAY_OF_WEEK,
    'NUTRITION_DISTRIBUTION': NUTRITION_DISTRIBUTION,
    'NUTRITION_RECENT_LOGS': NUTRITION_RECENT_LOGS,
    'NUTRITION_USER_TARGETS': NUTRITION_USER_TARGETS,
    # Sleep page queries
    'SLEEP_TOTAL_LOGS': SLEEP_TOTAL_LOGS,
    'SLEEP_AVG_DURATION': SLEEP_AVG_DURATION,
    'SLEEP_USERS_TRACKING': SLEEP_USERS_TRACKING,
    'SLEEP_USERS_WITH_TARGETS': SLEEP_USERS_WITH_TARGETS,
    'SLEEP_DURATION_TREND_AGG': SLEEP_DURATION_TREND_AGG,
    'SLEEP_BY_ACTIVITY_LEVEL': SLEEP_BY_ACTIVITY_LEVEL,
    'SLEEP_BY_DAY_OF_WEEK': SLEEP_BY_DAY_OF_WEEK,
    'SLEEP_USERS_EXCEEDING_TARGET': SLEEP_USERS_EXCEEDING_TARGET,
    'SLEEP_USERS_NEVER_LOGGED': SLEEP_USERS_NEVER_LOGGED,
    'SLEEP_RECENT_LOGS': SLEEP_RECENT_LOGS,
    # Weight page queries
    'WEIGHT_TOTAL_LOGS': WEIGHT_TOTAL_LOGS,
    'WEIGHT_AVG_WEIGHT': WEIGHT_AVG_WEIGHT,
    'WEIGHT_AVG_BODY_FAT': WEIGHT_AVG_BODY_FAT,
    'WEIGHT_USERS_TRACKING': WEIGHT_USERS_TRACKING,
    'WEIGHT_VS_BODY_FAT_JOINED': WEIGHT_VS_BODY_FAT_JOINED,
    'WEIGHT_DISTRIBUTION_BY_SEX_JOINED': WEIGHT_DISTRIBUTION_BY_SEX_JOINED,
    'WEIGHT_TREND_90D': WEIGHT_TREND_90D,
    'WEIGHT_BY_ACTIVITY_LEVEL': WEIGHT_BY_ACTIVITY_LEVEL,
    'WEIGHT_BODY_FAT_RANGES': WEIGHT_BODY_FAT_RANGES,
    'WEIGHT_USERS_WITH_GOALS': WEIGHT_USERS_WITH_GOALS,
}


def get_all_queries() -> dict:
    """Return all queries as a dictionary."""
    return QUERIES.copy()


def get_query_by_id(query_id: str) -> tuple:
    """
    Get a query by its ID.
    Returns (query_text, metadata) tuple or (None, None) if not found.
    """
    query = QUERIES.get(query_id)
    metadata = QUERY_METADATA.get(query_id)
    return query, metadata
