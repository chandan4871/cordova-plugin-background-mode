# ================================================================================
# Jenkins PowerShell Snippet - Add to Your Existing Script
# ================================================================================
# Insert this code block after detecting "esriJobSucceeded" status
# ================================================================================

if ($jobStatus -eq "esriJobSucceeded") {
    Write-Host "`n" + "="*80 -ForegroundColor Green
    Write-Host "✓ JOB COMPLETED SUCCESSFULLY!" -ForegroundColor Green
    Write-Host "="*80 -ForegroundColor Green
    
    # ============================================================================
    # METHOD 1: Read Summary File (FASTEST - Recommended)
    # ============================================================================
    $logDate = Get-Date -Format "yyyyMMdd"
    $summaryFile = "Y:\logfiles\GPLogs\${logDate}_Summary.txt"
    
    if (Test-Path $summaryFile) {
        Write-Host "`n📊 JOB SUMMARY:" -ForegroundColor Cyan
        Write-Host "="*80
        Get-Content $summaryFile
        Write-Host "="*80
    } else {
        Write-Host "⚠ Summary file not found, checking log file..." -ForegroundColor Yellow
        
        # ========================================================================
        # METHOD 2: Read from Main Log File (FALLBACK)
        # ========================================================================
        $logFile = "Y:\logfiles\GPLogs\${logDate}_GenerateInfrataggingSummaryIslandWide.log"
        
        if (Test-Path $logFile) {
            Write-Host "`n📄 LOG FILE SUMMARY:" -ForegroundColor Cyan
            Write-Host "="*80
            
            # Get last 30 lines and filter for summary
            Get-Content $logFile -Tail 30 | Where-Object { 
                $_ -match "FINAL SUMMARY|Depending Features|Supporting Features|Total Records|JOB COMPLETED" 
            } | ForEach-Object {
                # Highlight key metrics
                if ($_ -match "Depending|Supporting|Total Records") {
                    Write-Host $_ -ForegroundColor Green
                } else {
                    Write-Host $_
                }
            }
            
            Write-Host "="*80
            Write-Host "Full log: $logFile" -ForegroundColor Gray
        } else {
            Write-Host "❌ ERROR: Neither summary nor log file found!" -ForegroundColor Red
            Write-Host "Expected locations:" -ForegroundColor Yellow
            Write-Host "  Summary: $summaryFile" -ForegroundColor Yellow
            Write-Host "  Log: $logFile" -ForegroundColor Yellow
        }
    }
    
    # ============================================================================
    # METHOD 3: Verify Database Update (OPTIONAL)
    # ============================================================================
    Write-Host "`n💡 To verify database updates, run this SQL:" -ForegroundColor Cyan
    Write-Host @"
SELECT 
    COUNT(*) as Total_Records,
    MAX(UPDATEDDATE) as Last_Update,
    DATEDIFF(MINUTE, MAX(UPDATEDDATE), GETDATE()) as Minutes_Since_Update
FROM ONETOOLAPP.INFRATAGGING_SUMMARY_CACHE
"@ -ForegroundColor White
    
    Write-Host "`n" + "="*80 -ForegroundColor Green
    
    # Exit with success
    exit 0
}
elseif ($jobStatus -eq "esriJobFailed") {
    Write-Host "`n" + "="*80 -ForegroundColor Red
    Write-Host "✗ JOB FAILED!" -ForegroundColor Red
    Write-Host "="*80 -ForegroundColor Red
    
    # Check error summary file
    $logDate = Get-Date -Format "yyyyMMdd"
    $summaryFile = "Y:\logfiles\GPLogs\${logDate}_Summary.txt"
    
    if (Test-Path $summaryFile) {
        Write-Host "`n❌ ERROR SUMMARY:" -ForegroundColor Red
        Write-Host "="*80
        Get-Content $summaryFile
        Write-Host "="*80
    } else {
        # Fallback to log file
        $logFile = "Y:\logfiles\GPLogs\${logDate}_GenerateInfrataggingSummaryIslandWide.log"
        
        if (Test-Path $logFile) {
            Write-Host "`nLast 30 lines of log file:" -ForegroundColor Yellow
            Write-Host "="*80
            Get-Content $logFile -Tail 30
            Write-Host "="*80
        }
    }
    
    # Exit with error
    exit 1
}

# ================================================================================
# USAGE INSTRUCTIONS
# ================================================================================
<#

1. COPY THIS ENTIRE BLOCK

2. FIND THIS SECTION in your existing Jenkins PowerShell script:
   
   if ($jobStatus -eq "esriJobSucceeded") {
       Write-Host "Job completed successfully!"
   }

3. REPLACE IT with the code above

4. UPDATE THESE PATHS if different in your environment:
   - Y:\logfiles\GPLogs\  (Log folder path)
   - ONETOOLAPP.INFRATAGGING_SUMMARY_CACHE  (Table name)

5. TEST by running your Jenkins job

6. EXPECTED OUTPUT in Jenkins console:
   
   ================================================================================
   ✓ JOB COMPLETED SUCCESSFULLY!
   ================================================================================
   
   📊 JOB SUMMARY:
   ================================================================================
   JOB COMPLETED SUCCESSFULLY!
   ================================================================================
   Execution Time: 2025-11-25 15:10:58
   --------------------------------------------------------------------------------
   SUMMARY:
     - Depending Features Processed: 452
     - Supporting Features Processed: 346
     - Total Records Inserted: 798
   ================================================================================
   Log File: Y:\logfiles\GPLogs\20251125_GenerateInfrataggingSummaryIslandWide.log
   ================================================================================
   
   💡 To verify database updates, run this SQL:
   SELECT COUNT(*), MAX(UPDATEDDATE), DATEDIFF(MINUTE, MAX(UPDATEDDATE), GETDATE())
   FROM ONETOOLAPP.INFRATAGGING_SUMMARY_CACHE
   
   ================================================================================

#>

# ================================================================================
# FILE LOCATIONS EXPLAINED
# ================================================================================
<#

The Python script now creates TWO files:

1. SUMMARY FILE (Quick Read):
   Y:\logfiles\GPLogs\YYYYMMDD_Summary.txt
   - Small file (< 1 KB)
   - Contains ONLY the final summary
   - Perfect for Jenkins quick check
   - Created at job completion

2. LOG FILE (Detailed):
   Y:\logfiles\GPLogs\YYYYMMDD_GenerateInfrataggingSummaryIslandWide.log
   - Large file (can be MB)
   - Contains ALL execution details
   - Use for troubleshooting
   - Continuously updated during execution

PRIORITY: Try Summary File first → Fallback to Log File if not found

#>

# ================================================================================
# TROUBLESHOOTING
# ================================================================================
<#

PROBLEM: "Neither summary nor log file found!"
SOLUTION:
  1. Check if folder exists:
     Test-Path "Y:\logfiles\GPLogs"
  
  2. Check folder permissions:
     - ArcGIS Server account needs WRITE access
     - Jenkins account needs READ access
  
  3. Verify path in Python script:
     - Open GenerateInfrataggingSummaryIslandWide.py
     - Check LOG_FOLDER = "Y:\logfiles\GPLogs" (line 28)
     - Update if different

PROBLEM: "Summary file exists but is empty or old"
SOLUTION:
  1. Check file timestamp:
     (Get-Item $summaryFile).LastWriteTime
  
  2. If old, job might not have run or failed early
  
  3. Check main log file for errors:
     Get-Content $logFile -Tail 50

PROBLEM: "Job succeeds but no records in database"
SOLUTION:
  1. Check if table was truncated:
     SELECT COUNT(*) FROM ONETOOLAPP.INFRATAGGING_SUMMARY_CACHE
  
  2. Check for INSERT errors in log file:
     Get-Content $logFile | Select-String -Pattern "ERROR|Exception"
  
  3. Verify SDE connection is correct:
     - Check SDE_PATH in Python script
     - Test connection in ArcGIS Pro

#>
