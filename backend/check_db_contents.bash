#!/bin/bash

echo "=========================================="
echo " Personal Analytics - Database Contents"
echo "=========================================="
echo ""

# Set database connection
DB_NAME="personal_analytics"
DB_USER="analytics_user"
DB_HOST="localhost"

echo "Connecting to database: $DB_NAME"
echo "------------------------------------------"

psql -h $DB_HOST -U $DB_USER -d $DB_NAME -W << EOF

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
    SUM((daily_activities->>'work')::int) as work_days,
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
\\echo 'Database check complete!'
\\echo ''

EOF