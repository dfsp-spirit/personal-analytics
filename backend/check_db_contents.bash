#!/bin/bash
#
# Script to check and display contents of the PostgreSQL database used by the personal-analytics web app.
# This is a development script and is not intended for production use.
# It only reads data and does not modify anything, so it does not require sudo access.
# It uses the DATABASE_URL from the .env file to connect to the database.

echo "=== Personal Analytics - Check Database Contents ==="
echo "NOTE: This script is for development use only. It is not intended for production use."
echo "NOTE: You will need to start the backend at least once, so that the relations (tables) are created."

if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found. You need to create it first from the '.env.example' template file."
    exit 1
fi

source ".env"   # Loads environment variables DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD

# After sourcing the .env file, validate required variables
if [ -z "$DATABASE_NAME" ] || [ -z "$DATABASE_USER" ] || [ -z "$DATABASE_PASSWORD" ] || [ -z "$DATABASE_URL" ]; then
    echo "ERROR: Missing required database configuration in '.env' file."
    echo "Please ensure DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD, and DATABASE_URL are set."
    exit 1
fi

echo "Loaded env vars from '.env' file:"
echo " DATABASE_NAME='$DATABASE_NAME'"
echo " DATABASE_USER='$DATABASE_USER'"
echo " DATABASE_PASSWORD='(hidden)'"
echo " DATABASE_URL='(hidden)'"
## End of env file handling

# Set database connection

echo "Connecting to database: $DATABASE_NAME via DATABASE_URL..."
echo "------------------------------------------"


psql $DATABASE_URL << EOF

\\echo ''
\\echo '1. BASIC STATS'
\\echo '=================='
SELECT
    COUNT(*) as total_entries,
    MIN(date) as first_entry,
    MAX(date) as last_entry,
    ROUND(AVG(mood), 2) as avg_mood,
    ROUND(AVG(pain), 2) as avg_pain
FROM healthentry;

\\echo ''
\\echo '2. RECENT ENTRIES (last 5 days)'
\\echo '==================================='
SELECT date, mood, pain, allergy_state, sleep_quality
FROM healthentry
ORDER BY date DESC
LIMIT 5;

\\echo ''
\\echo '3. MOOD & PAIN CORRELATION'
\\echo '=============================='
SELECT
    ROUND(CORR(mood, pain)::numeric, 3) as mood_pain_correlation
FROM healthentry;

\\echo ''
\\echo '4. ACTIVITY BREAKDOWN'
\\echo '========================'
SELECT
    COUNT(*) as days_count,
    SUM((daily_activities->>'gaming')::int) as gaming_days,
    SUM((daily_activities->>'exercise')::int) as exercise_days,
    SUM((daily_activities->>'vacation')::int) as vacation_days,
    SUM((daily_activities->>'creative')::int) as creative_days
FROM healthentry;

\\echo ''
\\echo '5. LATEST FULL ENTRY'
\\echo '========================'
SELECT * FROM healthentry
ORDER BY date DESC
LIMIT 1;

\\echo ''
\\echo '6. ACTIVITIES ON HIGH PAIN DAYS (>7)'
\\echo '======================================='
SELECT
    date,
    pain,
    daily_activities->>'gaming' as gaming,
    daily_activities->>'exercise' as exercise,
    daily_activities->>'work' as work
FROM healthentry
WHERE pain > 7
ORDER BY pain DESC;


\\echo ''
\\echo '7. Average pain on weekends vs weekdays'
\\echo '======================================='
SELECT
    CASE WHEN day_of_week IN (5, 6) THEN 'weekend' ELSE 'weekday' END as day_type,
    AVG(pain) as avg_pain,
    AVG(mood) as avg_mood,
    COUNT(*) as days_count
FROM healthentry
GROUP BY day_type;


\\echo ''
\\echo '8. Pain by specific day of week'
\\echo '==============================='
SELECT
    day_of_week,
    AVG(pain) as avg_pain,
    AVG(mood) as avg_mood
FROM healthentry
GROUP BY day_of_week
ORDER BY day_of_week;

\\echo ''
\\echo '9. Worst pain days'
\\echo '=================='
SELECT
    CASE day_of_week
        WHEN 0 THEN 'Monday'
        WHEN 1 THEN 'Tuesday'
        WHEN 2 THEN 'Wednesday'
        WHEN 3 THEN 'Thursday'
        WHEN 4 THEN 'Friday'
        WHEN 5 THEN 'Saturday'
        WHEN 6 THEN 'Sunday'
    END as day_name,
    AVG(pain) as avg_pain
FROM healthentry
GROUP BY day_of_week
ORDER BY avg_pain DESC;

\\echo ''
\\echo 'Database check complete!'
\\echo ''

EOF