-- ================================================================================
-- SQL Script to Verify GenerateInfrataggingSummaryIslandWide Job Results
-- ================================================================================

-- Check 1: Verify table has data and get last update time
-- ================================================================================
SELECT 
    'LAST UPDATE CHECK' as Check_Type,
    COUNT(*) as Total_Records,
    MAX(UPDATEDDATE) as Last_Update_Time,
    DATEDIFF(MINUTE, MAX(UPDATEDDATE), GETDATE()) as Minutes_Since_Update
FROM ONETOOLAPP.INFRATAGGING_SUMMARY_CACHE;

-- Check 2: Get distribution by Type (Depending vs Supporting)
-- ================================================================================
SELECT 
    'TYPE DISTRIBUTION' as Check_Type,
    CASE 
        WHEN TYPE = 0 THEN 'Depending'
        WHEN TYPE = 1 THEN 'Supporting'
        ELSE 'Unknown'
    END as Feature_Type,
    COUNT(*) as Record_Count,
    AVG(CHARTHEIGHT) as Avg_Chart_Height
FROM ONETOOLAPP.INFRATAGGING_SUMMARY_CACHE
GROUP BY TYPE
ORDER BY TYPE;

-- Check 3: Get distribution by Category (Has Issues vs No Issues)
-- ================================================================================
SELECT 
    'CATEGORY DISTRIBUTION' as Check_Type,
    CASE 
        WHEN CATEGORY = 0 THEN 'No Issues'
        WHEN CATEGORY = 1 THEN 'Has Issues'
        ELSE 'Unknown'
    END as Issue_Status,
    CASE 
        WHEN TYPE = 0 THEN 'Depending'
        WHEN TYPE = 1 THEN 'Supporting'
        ELSE 'Unknown'
    END as Feature_Type,
    COUNT(*) as Record_Count
FROM ONETOOLAPP.INFRATAGGING_SUMMARY_CACHE
GROUP BY CATEGORY, TYPE
ORDER BY TYPE, CATEGORY;

-- Check 4: Sample records to verify data quality
-- ================================================================================
SELECT TOP 5
    'SAMPLE DEPENDING RECORDS' as Check_Type,
    LAYER as Layer_Name,
    LAYER_ID,
    FEATUREID,
    CASE WHEN CATEGORY = 0 THEN 'No Issues' ELSE 'Has Issues' END as Status,
    CHARTHEIGHT,
    LEN(CHARTJSON) as ChartJSON_Length,
    CASE 
        WHEN CHARTJSON IS NULL THEN 'NULL'
        WHEN LEN(CHARTJSON) < 100 THEN 'Too Short (Likely Empty)'
        ELSE 'Valid'
    END as ChartJSON_Status,
    UPDATEDDATE
FROM ONETOOLAPP.INFRATAGGING_SUMMARY_CACHE
WHERE TYPE = 0  -- Depending
ORDER BY UPDATEDDATE DESC;

SELECT TOP 5
    'SAMPLE SUPPORTING RECORDS' as Check_Type,
    LAYER as Layer_Name,
    LAYER_ID,
    FEATUREID,
    CASE WHEN CATEGORY = 0 THEN 'No Issues' ELSE 'Has Issues' END as Status,
    CHARTHEIGHT,
    LEN(CHARTJSON) as ChartJSON_Length,
    CASE 
        WHEN CHARTJSON IS NULL THEN 'NULL'
        WHEN LEN(CHARTJSON) < 100 THEN 'Too Short (Likely Empty)'
        ELSE 'Valid'
    END as ChartJSON_Status,
    UPDATEDDATE
FROM ONETOOLAPP.INFRATAGGING_SUMMARY_CACHE
WHERE TYPE = 1  -- Supporting
ORDER BY UPDATEDDATE DESC;

-- Check 5: Identify potential issues
-- ================================================================================
SELECT 
    'DATA QUALITY ISSUES' as Check_Type,
    SUM(CASE WHEN LAYER_ID = -1 THEN 1 ELSE 0 END) as Invalid_Layer_ID_Count,
    SUM(CASE WHEN CHARTJSON IS NULL THEN 1 ELSE 0 END) as Null_ChartJSON_Count,
    SUM(CASE WHEN LEN(CHARTJSON) < 100 THEN 1 ELSE 0 END) as Empty_ChartJSON_Count,
    SUM(CASE WHEN CHARTHEIGHT = 100 THEN 1 ELSE 0 END) as Default_ChartHeight_Count
FROM ONETOOLAPP.INFRATAGGING_SUMMARY_CACHE;

-- Check 6: Records with issues (CATEGORY = 1)
-- ================================================================================
SELECT 
    'RECORDS WITH ISSUES' as Check_Type,
    LAYER as Layer_Name,
    LAYER_ID,
    FEATUREID,
    CASE WHEN TYPE = 0 THEN 'Depending' ELSE 'Supporting' END as Feature_Type,
    CHARTHEIGHT,
    UPDATEDDATE
FROM ONETOOLAPP.INFRATAGGING_SUMMARY_CACHE
WHERE CATEGORY = 1
ORDER BY TYPE, LAYER, FEATUREID;

-- Check 7: Verify ChartJSON contains valid data (not empty or null)
-- ================================================================================
SELECT TOP 10
    'CHARTJSON VALIDATION' as Check_Type,
    LAYER as Layer_Name,
    FEATUREID,
    CASE WHEN TYPE = 0 THEN 'Depending' ELSE 'Supporting' END as Feature_Type,
    CHARTHEIGHT,
    LEFT(CHARTJSON, 200) as ChartJSON_Preview,  -- First 200 chars
    LEN(CHARTJSON) as Full_Length,
    UPDATEDDATE
FROM ONETOOLAPP.INFRATAGGING_SUMMARY_CACHE
WHERE CHARTJSON IS NOT NULL 
  AND LEN(CHARTJSON) > 100
ORDER BY UPDATEDDATE DESC;

-- ================================================================================
-- EXPECTED RESULTS GUIDE
-- ================================================================================
/*

✓ SUCCESSFUL JOB SHOULD SHOW:
-------------------------------
1. Last_Update_Time within last few minutes
2. Total_Records matching expected counts (e.g., 452 Depending + 346 Supporting = 798)
3. Both "Depending" (TYPE=0) and "Supporting" (TYPE=1) records
4. Both "No Issues" (CATEGORY=0) and "Has Issues" (CATEGORY=1) records
5. No NULL ChartJSON values
6. ChartJSON_Length > 500 (indicates proper chart data)
7. CHARTHEIGHT > 100 for records with dependencies
8. LAYER_ID != -1 (valid layer matching)

❌ ISSUES TO INVESTIGATE:
--------------------------
- Minutes_Since_Update > 120 → Job might not have run
- Invalid_Layer_ID_Count > 0 → Layer matching failed
- Null_ChartJSON_Count > 0 → Chart generation failed
- Empty_ChartJSON_Count > 0 → Chart data missing
- Default_ChartHeight_Count = Total_Records → No dependencies processed
- No records with CATEGORY = 1 → Issue detection not working

*/

-- ================================================================================
-- QUICK ONE-LINER FOR JENKINS
-- ================================================================================
-- Use this in Jenkins to quickly verify:

SELECT 
    COUNT(*) as Total,
    MAX(UPDATEDDATE) as LastUpdate,
    SUM(CASE WHEN CATEGORY=1 THEN 1 ELSE 0 END) as HasIssues,
    AVG(CHARTHEIGHT) as AvgHeight,
    DATEDIFF(MINUTE, MAX(UPDATEDDATE), GETDATE()) as MinAgo
FROM ONETOOLAPP.INFRATAGGING_SUMMARY_CACHE;

-- Expected: Total > 0, LastUpdate recent, HasIssues > 0, AvgHeight > 100, MinAgo < 30
