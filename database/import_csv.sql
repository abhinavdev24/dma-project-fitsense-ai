-- ============================================================
-- FitSense AI — Load Data Statements
-- ============================================================
-- Base path: /Users/abhinav/Developer/NEU/mlops/FitSenseAI/Data-Pipeline/data/raw
-- Run this file from MySQL Workbench after enabling local_infile:
--   SET GLOBAL local_infile = 1;
-- ============================================================
SET GLOBAL local_infile = 1;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- Helper macro (inline): all UUID columns use UNHEX(REPLACE(...))
-- All datetime columns use CONVERT_TZ(..., '+00:00', '+00:00')
-- Blank rows are skipped via IF(@col = '', NULL, ...)
-- ============================================================


-- ------------------------------------------------------------
-- users
-- synthetic_profiles/20260308T234033Z/users.csv
-- columns: user_id, name, email, created_at
-- ------------------------------------------------------------
LOAD DATA LOCAL INFILE '/Users/abhinav/Developer/NEU/mlops/FitSenseAI/Data-Pipeline/data/raw/synthetic_profiles/20260308T234033Z/users.csv'
INTO TABLE users
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@user_id, name, email, @created_at)
SET
  user_id    = IF(@user_id    = '', NULL, UNHEX(REPLACE(@user_id, '-', ''))),
  created_at = IF(@created_at = '', NULL, CONVERT_TZ(@created_at, '+00:00', '+00:00'));
DELETE FROM users WHERE user_id IS NULL;


-- ------------------------------------------------------------
-- goals
-- synthetic_profiles/20260308T234033Z/goals.csv
-- columns: goal_id, name, description
-- ------------------------------------------------------------
LOAD DATA LOCAL INFILE '/Users/abhinav/Developer/NEU/mlops/FitSenseAI/Data-Pipeline/data/raw/synthetic_profiles/20260308T234033Z/goals.csv'
INTO TABLE goals
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@goal_id, name, description)
SET
  goal_id = IF(@goal_id = '', NULL, UNHEX(REPLACE(@goal_id, '-', '')));
DELETE FROM goals WHERE goal_id IS NULL;


-- ------------------------------------------------------------
-- user_goals
-- synthetic_profiles/20260308T234033Z/user_goals.csv
-- columns: user_id, goal_id, priority
-- ------------------------------------------------------------
LOAD DATA LOCAL INFILE '/Users/abhinav/Developer/NEU/mlops/FitSenseAI/Data-Pipeline/data/raw/synthetic_profiles/20260308T234033Z/user_goals.csv'
INTO TABLE user_goals
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@user_id, @goal_id, priority)
SET
  user_id = IF(@user_id = '', NULL, UNHEX(REPLACE(@user_id, '-', ''))),
  goal_id = IF(@goal_id = '', NULL, UNHEX(REPLACE(@goal_id, '-', '')));
DELETE FROM user_goals WHERE user_id IS NULL;


-- ------------------------------------------------------------
-- conditions
-- synthetic_profiles/20260308T234033Z/conditions.csv
-- columns: condition_id, name, description
-- ------------------------------------------------------------
LOAD DATA LOCAL INFILE '/Users/abhinav/Developer/NEU/mlops/FitSenseAI/Data-Pipeline/data/raw/synthetic_profiles/20260308T234033Z/conditions.csv'
INTO TABLE conditions
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@condition_id, name, description)
SET
  condition_id = IF(@condition_id = '', NULL, UNHEX(REPLACE(@condition_id, '-', '')));
DELETE FROM conditions WHERE condition_id IS NULL;


-- ------------------------------------------------------------
-- user_conditions
-- synthetic_profiles/20260308T234033Z/user_conditions.csv
-- columns: user_id, condition_id, severity, notes
-- ------------------------------------------------------------
LOAD DATA LOCAL INFILE '/Users/abhinav/Developer/NEU/mlops/FitSenseAI/Data-Pipeline/data/raw/synthetic_profiles/20260308T234033Z/user_conditions.csv'
INTO TABLE user_conditions
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@user_id, @condition_id, severity, notes)
SET
  user_id      = IF(@user_id      = '', NULL, UNHEX(REPLACE(@user_id,      '-', ''))),
  condition_id = IF(@condition_id = '', NULL, UNHEX(REPLACE(@condition_id, '-', '')));
DELETE FROM user_conditions WHERE user_id IS NULL;


-- ------------------------------------------------------------
-- user_profiles
-- synthetic_profiles/20260308T234033Z/user_profiles.csv
-- columns: user_id, date_of_birth, sex, height_cm, activity_level, updated_at
-- ------------------------------------------------------------
LOAD DATA LOCAL INFILE '/Users/abhinav/Developer/NEU/mlops/FitSenseAI/Data-Pipeline/data/raw/synthetic_profiles/20260308T234033Z/user_profiles.csv'
INTO TABLE user_profiles
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@user_id, date_of_birth, sex, height_cm, activity_level, @updated_at)
SET
  user_id    = IF(@user_id    = '', NULL, UNHEX(REPLACE(@user_id, '-', ''))),
  updated_at = IF(@updated_at = '', NULL, CONVERT_TZ(@updated_at, '+00:00', '+00:00'));
DELETE FROM user_profiles WHERE user_id IS NULL;


-- ------------------------------------------------------------
-- user_medical_profiles
-- synthetic_profiles/20260308T234033Z/user_medical_profiles.csv
-- columns: medical_profile_id, user_id, has_injuries, injury_details,
--          surgeries_history, family_history, notes, updated_at
-- ------------------------------------------------------------
LOAD DATA LOCAL INFILE '/Users/abhinav/Developer/NEU/mlops/FitSenseAI/Data-Pipeline/data/raw/synthetic_profiles/20260308T234033Z/user_medical_profiles.csv'
INTO TABLE user_medical_profiles
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@medical_profile_id, @user_id, has_injuries, injury_details, surgeries_history, family_history, notes, @updated_at)
SET
  medical_profile_id = IF(@medical_profile_id = '', NULL, UNHEX(REPLACE(@medical_profile_id, '-', ''))),
  user_id            = IF(@user_id            = '', NULL, UNHEX(REPLACE(@user_id,            '-', ''))),
  updated_at         = IF(@updated_at         = '', NULL, CONVERT_TZ(@updated_at, '+00:00', '+00:00'));
DELETE FROM user_medical_profiles WHERE medical_profile_id IS NULL;


-- ------------------------------------------------------------
-- user_medications
-- synthetic_profiles/20260308T234033Z/user_medications.csv
-- columns: medication_id, user_id, medication_name, dosage,
--          frequency, start_date, end_date, notes
-- ------------------------------------------------------------
LOAD DATA LOCAL INFILE '/Users/abhinav/Developer/NEU/mlops/FitSenseAI/Data-Pipeline/data/raw/synthetic_profiles/20260308T234033Z/user_medications.csv'
INTO TABLE user_medications
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@medication_id, @user_id, medication_name, dosage, frequency, start_date, end_date, notes)
SET
  medication_id = IF(@medication_id = '', NULL, UNHEX(REPLACE(@medication_id, '-', ''))),
  user_id       = IF(@user_id       = '', NULL, UNHEX(REPLACE(@user_id,       '-', '')));
DELETE FROM user_medications WHERE medication_id IS NULL;


-- ------------------------------------------------------------
-- user_allergies
-- synthetic_profiles/20260308T234033Z/user_allergies.csv
-- columns: allergy_id, user_id, allergen, reaction, severity, notes
-- ------------------------------------------------------------
LOAD DATA LOCAL INFILE '/Users/abhinav/Developer/NEU/mlops/FitSenseAI/Data-Pipeline/data/raw/synthetic_profiles/20260308T234033Z/user_allergies.csv'
INTO TABLE user_allergies
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@allergy_id, @user_id, allergen, reaction, severity, notes)
SET
  allergy_id = IF(@allergy_id = '', NULL, UNHEX(REPLACE(@allergy_id, '-', ''))),
  user_id    = IF(@user_id    = '', NULL, UNHEX(REPLACE(@user_id,    '-', '')));
DELETE FROM user_allergies WHERE allergy_id IS NULL;


-- ------------------------------------------------------------
-- calorie_targets
-- synthetic_profiles/20260308T234033Z/calorie_targets.csv
-- columns: calorie_target_id, user_id, maintenance_calories, method,
--          effective_from, effective_to, notes, created_at
-- ------------------------------------------------------------
LOAD DATA LOCAL INFILE '/Users/abhinav/Developer/NEU/mlops/FitSenseAI/Data-Pipeline/data/raw/synthetic_profiles/20260308T234033Z/calorie_targets.csv'
INTO TABLE calorie_targets
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@calorie_target_id, @user_id, maintenance_calories, method, effective_from, effective_to, notes, @created_at)
SET
  calorie_target_id = IF(@calorie_target_id = '', NULL, UNHEX(REPLACE(@calorie_target_id, '-', ''))),
  user_id           = IF(@user_id           = '', NULL, UNHEX(REPLACE(@user_id,           '-', ''))),
  created_at        = IF(@created_at        = '', NULL, CONVERT_TZ(@created_at, '+00:00', '+00:00'));
DELETE FROM calorie_targets WHERE calorie_target_id IS NULL;


-- ------------------------------------------------------------
-- sleep_targets
-- synthetic_profiles/20260308T234033Z/sleep_targets.csv
-- columns: sleep_target_id, user_id, target_sleep_hours,
--          effective_from, effective_to, notes, created_at
-- ------------------------------------------------------------
LOAD DATA LOCAL INFILE '/Users/abhinav/Developer/NEU/mlops/FitSenseAI/Data-Pipeline/data/raw/synthetic_profiles/20260308T234033Z/sleep_targets.csv'
INTO TABLE sleep_targets
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@sleep_target_id, @user_id, target_sleep_hours, effective_from, effective_to, notes, @created_at)
SET
  sleep_target_id = IF(@sleep_target_id = '', NULL, UNHEX(REPLACE(@sleep_target_id, '-', ''))),
  user_id         = IF(@user_id         = '', NULL, UNHEX(REPLACE(@user_id,         '-', ''))),
  created_at      = IF(@created_at      = '', NULL, CONVERT_TZ(@created_at, '+00:00', '+00:00'));
DELETE FROM sleep_targets WHERE sleep_target_id IS NULL;


-- ------------------------------------------------------------
-- equipment
-- synthetic_workouts/20260308T234040Z/equipment.csv
-- columns: equipment_id, name, category
-- ------------------------------------------------------------
LOAD DATA LOCAL INFILE '/Users/abhinav/Developer/NEU/mlops/FitSenseAI/Data-Pipeline/data/raw/synthetic_workouts/20260308T234040Z/equipment.csv'
INTO TABLE equipment
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@equipment_id, name, category)
SET
  equipment_id = IF(@equipment_id = '', NULL, UNHEX(REPLACE(@equipment_id, '-', '')));
DELETE FROM equipment WHERE equipment_id IS NULL;


-- ------------------------------------------------------------
-- exercises
-- synthetic_workouts/20260308T234040Z/exercises.csv
-- columns: exercise_id, name, primary_muscle, notes, video_url, thumbnail_base64
-- ------------------------------------------------------------
LOAD DATA LOCAL INFILE '/Users/abhinav/Developer/NEU/mlops/FitSenseAI/Data-Pipeline/data/raw/synthetic_workouts/20260308T234040Z/exercises.csv'
INTO TABLE exercises
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@exercise_id, name, primary_muscle, notes, video_url, thumbnail_base64)
SET
  exercise_id = IF(@exercise_id = '', NULL, UNHEX(REPLACE(@exercise_id, '-', '')));
DELETE FROM exercises WHERE exercise_id IS NULL;


-- ------------------------------------------------------------
-- exercise_equipment
-- synthetic_workouts/20260308T234040Z/exercise_equipment.csv
-- columns: exercise_id, equipment_id
-- ------------------------------------------------------------
LOAD DATA LOCAL INFILE '/Users/abhinav/Developer/NEU/mlops/FitSenseAI/Data-Pipeline/data/raw/synthetic_workouts/20260308T234040Z/exercise_equipment.csv'
INTO TABLE exercise_equipment
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@exercise_id, @equipment_id)
SET
  exercise_id  = IF(@exercise_id  = '', NULL, UNHEX(REPLACE(@exercise_id,  '-', ''))),
  equipment_id = IF(@equipment_id = '', NULL, UNHEX(REPLACE(@equipment_id, '-', '')));
DELETE FROM exercise_equipment WHERE exercise_id IS NULL;


-- ------------------------------------------------------------
-- workout_plans
-- synthetic_workouts/20260308T234040Z/workout_plans.csv
-- columns: plan_id, user_id, name, is_active, created_at
-- ------------------------------------------------------------
LOAD DATA LOCAL INFILE '/Users/abhinav/Developer/NEU/mlops/FitSenseAI/Data-Pipeline/data/raw/synthetic_workouts/20260308T234040Z/workout_plans.csv'
INTO TABLE workout_plans
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@plan_id, @user_id, name, is_active, @created_at)
SET
  plan_id    = IF(@plan_id    = '', NULL, UNHEX(REPLACE(@plan_id,    '-', ''))),
  user_id    = IF(@user_id    = '', NULL, UNHEX(REPLACE(@user_id,    '-', ''))),
  created_at = IF(@created_at = '', NULL, CONVERT_TZ(@created_at, '+00:00', '+00:00'));
DELETE FROM workout_plans WHERE plan_id IS NULL;


-- ------------------------------------------------------------
-- plan_days
-- synthetic_workouts/20260308T234040Z/plan_days.csv
-- columns: plan_day_id, plan_id, name, day_order, notes
-- ------------------------------------------------------------
LOAD DATA LOCAL INFILE '/Users/abhinav/Developer/NEU/mlops/FitSenseAI/Data-Pipeline/data/raw/synthetic_workouts/20260308T234040Z/plan_days.csv'
INTO TABLE plan_days
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@plan_day_id, @plan_id, name, day_order, notes)
SET
  plan_day_id = IF(@plan_day_id = '', NULL, UNHEX(REPLACE(@plan_day_id, '-', ''))),
  plan_id     = IF(@plan_id     = '', NULL, UNHEX(REPLACE(@plan_id,     '-', '')));
DELETE FROM plan_days WHERE plan_day_id IS NULL;


-- ------------------------------------------------------------
-- plan_exercises
-- synthetic_workouts/20260308T234040Z/plan_exercises.csv
-- columns: plan_exercise_id, plan_day_id, exercise_id, position, notes
-- ------------------------------------------------------------
LOAD DATA LOCAL INFILE '/Users/abhinav/Developer/NEU/mlops/FitSenseAI/Data-Pipeline/data/raw/synthetic_workouts/20260308T234040Z/plan_exercises.csv'
INTO TABLE plan_exercises
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@plan_exercise_id, @plan_day_id, @exercise_id, position, notes)
SET
  plan_exercise_id = IF(@plan_exercise_id = '', NULL, UNHEX(REPLACE(@plan_exercise_id, '-', ''))),
  plan_day_id      = IF(@plan_day_id      = '', NULL, UNHEX(REPLACE(@plan_day_id,      '-', ''))),
  exercise_id      = IF(@exercise_id      = '', NULL, UNHEX(REPLACE(@exercise_id,      '-', '')));
DELETE FROM plan_exercises WHERE plan_exercise_id IS NULL;


-- ------------------------------------------------------------
-- plan_sets
-- synthetic_workouts/20260308T234040Z/plan_sets.csv
-- columns: plan_set_id, plan_exercise_id, set_number, target_reps,
--          target_weight, target_rir, rest_seconds
-- ------------------------------------------------------------
LOAD DATA LOCAL INFILE '/Users/abhinav/Developer/NEU/mlops/FitSenseAI/Data-Pipeline/data/raw/synthetic_workouts/20260308T234040Z/plan_sets.csv'
INTO TABLE plan_sets
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@plan_set_id, @plan_exercise_id, set_number, target_reps, target_weight, target_rir, rest_seconds)
SET
  plan_set_id      = IF(@plan_set_id      = '', NULL, UNHEX(REPLACE(@plan_set_id,      '-', ''))),
  plan_exercise_id = IF(@plan_exercise_id = '', NULL, UNHEX(REPLACE(@plan_exercise_id, '-', '')));
DELETE FROM plan_sets WHERE plan_set_id IS NULL;


-- ------------------------------------------------------------
-- workouts
-- synthetic_workouts/20260308T234040Z/workouts.csv
-- columns: workout_id, user_id, plan_id, plan_day_id,
--          started_at, ended_at, notes
-- ------------------------------------------------------------
LOAD DATA LOCAL INFILE '/Users/abhinav/Developer/NEU/mlops/FitSenseAI/Data-Pipeline/data/raw/synthetic_workouts/20260308T234040Z/workouts.csv'
INTO TABLE workouts
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@workout_id, @user_id, @plan_id, @plan_day_id, @started_at, @ended_at, notes)
SET
  workout_id  = IF(@workout_id  = '', NULL, UNHEX(REPLACE(@workout_id,  '-', ''))),
  user_id     = IF(@user_id     = '', NULL, UNHEX(REPLACE(@user_id,     '-', ''))),
  plan_id     = IF(@plan_id     = '', NULL, UNHEX(REPLACE(@plan_id,     '-', ''))),
  plan_day_id = IF(@plan_day_id = '', NULL, UNHEX(REPLACE(@plan_day_id, '-', ''))),
  started_at  = IF(@started_at  = '', NULL, CONVERT_TZ(@started_at,  '+00:00', '+00:00')),
  ended_at    = IF(@ended_at    = '', NULL, CONVERT_TZ(@ended_at,    '+00:00', '+00:00'));
DELETE FROM workouts WHERE workout_id IS NULL;


-- ------------------------------------------------------------
-- workout_exercises
-- synthetic_workouts/20260308T234040Z/workout_exercises.csv
-- columns: workout_exercise_id, workout_id, exercise_id,
--          plan_exercise_id, position, notes
-- ------------------------------------------------------------
LOAD DATA LOCAL INFILE '/Users/abhinav/Developer/NEU/mlops/FitSenseAI/Data-Pipeline/data/raw/synthetic_workouts/20260308T234040Z/workout_exercises.csv'
INTO TABLE workout_exercises
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@workout_exercise_id, @workout_id, @exercise_id, @plan_exercise_id, position, notes)
SET
  workout_exercise_id = IF(@workout_exercise_id = '', NULL, UNHEX(REPLACE(@workout_exercise_id, '-', ''))),
  workout_id          = IF(@workout_id          = '', NULL, UNHEX(REPLACE(@workout_id,          '-', ''))),
  exercise_id         = IF(@exercise_id         = '', NULL, UNHEX(REPLACE(@exercise_id,         '-', ''))),
  plan_exercise_id    = IF(@plan_exercise_id    = '', NULL, UNHEX(REPLACE(@plan_exercise_id,    '-', '')));
DELETE FROM workout_exercises WHERE workout_exercise_id IS NULL;


-- ------------------------------------------------------------
-- workout_sets
-- synthetic_workouts/20260308T234040Z/workout_sets.csv
-- columns: workout_set_id, workout_exercise_id, set_number, reps,
--          weight, rir, is_warmup, completed_at
-- ------------------------------------------------------------
LOAD DATA LOCAL INFILE '/Users/abhinav/Developer/NEU/mlops/FitSenseAI/Data-Pipeline/data/raw/synthetic_workouts/20260308T234040Z/workout_sets.csv'
INTO TABLE workout_sets
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@workout_set_id, @workout_exercise_id, set_number, reps, weight, rir, is_warmup, @completed_at)
SET
  workout_set_id      = IF(@workout_set_id      = '', NULL, UNHEX(REPLACE(@workout_set_id,      '-', ''))),
  workout_exercise_id = IF(@workout_exercise_id = '', NULL, UNHEX(REPLACE(@workout_exercise_id, '-', ''))),
  completed_at        = IF(@completed_at        = '', NULL, CONVERT_TZ(@completed_at, '+00:00', '+00:00'));
DELETE FROM workout_sets WHERE workout_set_id IS NULL;


-- ------------------------------------------------------------
-- calorie_intake_logs
-- synthetic_workouts/20260308T234040Z/calorie_intake_logs.csv
-- columns: calorie_log_id, user_id, log_date, calories_consumed,
--          notes, created_at
-- ------------------------------------------------------------
LOAD DATA LOCAL INFILE '/Users/abhinav/Developer/NEU/mlops/FitSenseAI/Data-Pipeline/data/raw/synthetic_workouts/20260308T234040Z/calorie_intake_logs.csv'
INTO TABLE calorie_intake_logs
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@calorie_log_id, @user_id, log_date, calories_consumed, notes, @created_at)
SET
  calorie_log_id = IF(@calorie_log_id = '', NULL, UNHEX(REPLACE(@calorie_log_id, '-', ''))),
  user_id        = IF(@user_id        = '', NULL, UNHEX(REPLACE(@user_id,        '-', ''))),
  created_at     = IF(@created_at     = '', NULL, CONVERT_TZ(@created_at, '+00:00', '+00:00'));
DELETE FROM calorie_intake_logs WHERE calorie_log_id IS NULL;


-- ------------------------------------------------------------
-- sleep_duration_logs
-- synthetic_workouts/20260308T234040Z/sleep_duration_logs.csv
-- columns: sleep_log_id, user_id, log_date, sleep_duration_hours,
--          notes, created_at
-- ------------------------------------------------------------
LOAD DATA LOCAL INFILE '/Users/abhinav/Developer/NEU/mlops/FitSenseAI/Data-Pipeline/data/raw/synthetic_workouts/20260308T234040Z/sleep_duration_logs.csv'
INTO TABLE sleep_duration_logs
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@sleep_log_id, @user_id, log_date, sleep_duration_hours, notes, @created_at)
SET
  sleep_log_id = IF(@sleep_log_id = '', NULL, UNHEX(REPLACE(@sleep_log_id, '-', ''))),
  user_id      = IF(@user_id      = '', NULL, UNHEX(REPLACE(@user_id,      '-', ''))),
  created_at   = IF(@created_at   = '', NULL, CONVERT_TZ(@created_at, '+00:00', '+00:00'));
DELETE FROM sleep_duration_logs WHERE sleep_log_id IS NULL;


-- ------------------------------------------------------------
-- weight_logs
-- synthetic_workouts/20260308T234040Z/weight_logs.csv
-- columns: weight_log_id, user_id, logged_at, weight_kg,
--          body_fat_percentage, notes
-- ------------------------------------------------------------
LOAD DATA LOCAL INFILE '/Users/abhinav/Developer/NEU/mlops/FitSenseAI/Data-Pipeline/data/raw/synthetic_workouts/20260308T234040Z/weight_logs.csv'
INTO TABLE weight_logs
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@weight_log_id, @user_id, @logged_at, weight_kg, body_fat_percentage, notes)
SET
  weight_log_id = IF(@weight_log_id = '', NULL, UNHEX(REPLACE(@weight_log_id, '-', ''))),
  user_id       = IF(@user_id       = '', NULL, UNHEX(REPLACE(@user_id,       '-', ''))),
  logged_at     = IF(@logged_at     = '', NULL, CONVERT_TZ(@logged_at, '+00:00', '+00:00'));
DELETE FROM weight_logs WHERE weight_log_id IS NULL;


SET FOREIGN_KEY_CHECKS = 1;