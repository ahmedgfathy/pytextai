
-- Sample SQL Queries for Real Estate Database
-- File: sample_queries.sql

-- 1. Get total number of properties
SELECT COUNT(*) as total_properties FROM properties;

-- 2. Get properties by region
SELECT region, COUNT(*) as count 
FROM properties 
WHERE region != '' 
GROUP BY region 
ORDER BY count DESC;

-- 3. Get properties by type
SELECT property_type, COUNT(*) as count 
FROM properties 
WHERE property_type != '' 
GROUP BY property_type 
ORDER BY count DESC;

-- 4. Get most active senders
SELECT sender_name, COUNT(*) as messages_count
FROM properties 
WHERE sender_name != ''
GROUP BY sender_name 
ORDER BY messages_count DESC 
LIMIT 20;

-- 5. Search for properties containing specific keywords
SELECT unique_id, sender_name, region, property_type, message
FROM properties 
WHERE message LIKE '%شقة%' OR message LIKE '%apartment%'
LIMIT 50;

-- 6. Get properties by date range
SELECT date, COUNT(*) as count
FROM properties 
WHERE date != ''
GROUP BY date 
ORDER BY date DESC;

-- 7. Find properties with phone numbers
SELECT sender_name, sender_phone, message
FROM properties 
WHERE sender_phone != '' AND sender_phone != 'nan'
LIMIT 20;

-- 8. Get file source statistics
SELECT file_source, COUNT(*) as count
FROM properties 
GROUP BY file_source 
ORDER BY count DESC;

-- 9. Advanced search with multiple criteria
SELECT *
FROM properties 
WHERE region LIKE '%القاهرة%' 
  AND property_type != ''
  AND message LIKE '%للبيع%'
LIMIT 30;

-- 10. Get recent entries (if date format is consistent)
SELECT *
FROM properties 
WHERE created_at >= datetime('now', '-30 days')
ORDER BY created_at DESC;
