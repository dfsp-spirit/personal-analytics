#!/bin/bash

echo "=========================================="
echo " Personal Analytics - Database Contents"
echo "=========================================="
echo ""

source .env   # Load DB credentials from .env

# Set database connection

echo "Connecting to database: $DATABASE_NAME"
echo "------------------------------------------"

#psql -h $DB_HOST -U $DB_USER -d $DB_NAME -W << EOF
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