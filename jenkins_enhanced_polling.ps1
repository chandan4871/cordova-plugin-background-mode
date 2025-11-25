# ================================================================================
# Enhanced Jenkins PowerShell Script for ArcGIS Server GP Job with Message Retrieval
# ================================================================================

param(
    [string]$ServerUrl = "https://3.gis.gov.sg/onetool/rest/services/ONETOOL_GPTOOLS/GenerateInfrataggingSummaryIslandWide/GPServer/GenerateInfrataggingSummaryIslandWide",
    [string]$LogPath = "Y:\logfiles\GPLogs",
    [int]$PollInterval = 10
)

# ================================================================================
# CONFIGURATION
# ================================================================================

$submitUrl = "$ServerUrl/submitJob"
$baseUrl = $ServerUrl

# ================================================================================
# STEP 1: SUBMIT JOB
# ================================================================================

Write-Host "Submitting the job to ArcGIS server..."
$submitResponse = Invoke-RestMethod -Uri "$submitUrl?f=json" -Method POST

Write-Host "Full Response: "
$submitResponse

if (-not $submitResponse.jobId) {
    Write-Host "ERROR: Failed to submit job. No jobId returned." -ForegroundColor Red
    exit 1
}

$jobId = $submitResponse.jobId
Write-Host "`nJob successfully submitted. Job ID: $jobId" -ForegroundColor Green

# ================================================================================
# STEP 2: POLL JOB STATUS
# ================================================================================

Write-Host "Polling job status. Full URL: $baseUrl/jobs/$jobId`?f=json"

$jobStatus = ""
$statusUrl = "$baseUrl/jobs/$jobId"
$pollCount = 0
$maxPolls = 360  # Max 1 hour (360 * 10 seconds)

while ($jobStatus -ne "esriJobSucceeded" -and $jobStatus -ne "esriJobFailed" -and $pollCount -lt $maxPolls) {
    Start-Sleep -Seconds $PollInterval
    $pollCount++
    
    Write-Host "`nPolling job status (Attempt $pollCount)..."
    
    try {
        $statusResponse = Invoke-RestMethod -Uri "$statusUrl?f=json" -Method POST
        
        Write-Host "Full Status Response:"
        $statusResponse | ConvertTo-Json -Depth 10
        
        $jobStatus = $statusResponse.jobStatus
        Write-Host "`nCurrent Job Status: $jobStatus" -ForegroundColor $(
            if ($jobStatus -eq "esriJobSucceeded") { "Green" } 
            elseif ($jobStatus -eq "esriJobFailed") { "Red" } 
            else { "Yellow" }
        )
        
        # Show progress if available
        if ($statusResponse.progress) {
            Write-Host "Progress: $($statusResponse.progress.message)" -ForegroundColor Cyan
        }
        
        # Show any messages during execution
        if ($statusResponse.messages -and $statusResponse.messages.Count -gt 0) {
            Write-Host "`nExecution Messages:" -ForegroundColor Cyan
            foreach ($msg in $statusResponse.messages) {
                $color = switch ($msg.type) {
                    "esriJobMessageTypeInformative" { "White" }
                    "esriJobMessageTypeWarning" { "Yellow" }
                    "esriJobMessageTypeError" { "Red" }
                    default { "Gray" }
                }
                Write-Host "  [$($msg.type)] $($msg.description)" -ForegroundColor $color
            }
        }
        
    } catch {
        Write-Host "Error polling job status: $_" -ForegroundColor Red
    }
}

# ================================================================================
# STEP 3: CHECK FINAL STATUS
# ================================================================================

if ($jobStatus -eq "esriJobSucceeded") {
    Write-Host "`n" + "="*80 -ForegroundColor Green
    Write-Host "✓ JOB COMPLETED SUCCESSFULLY!" -ForegroundColor Green
    Write-Host "="*80 -ForegroundColor Green
    
    # ============================================================================
    # STEP 4: RETRIEVE MESSAGES FROM MULTIPLE SOURCES
    # ============================================================================
    
    # Try Method 1: Messages Endpoint
    Write-Host "`nMethod 1: Checking Messages Endpoint..."
    try {
        $messagesUrl = "$baseUrl/jobs/$jobId/messages?f=json"
        $messagesResponse = Invoke-RestMethod -Uri $messagesUrl -Method POST
        
        if ($messagesResponse.messages -and $messagesResponse.messages.Count -gt 0) {
            Write-Host "`n📨 JOB MESSAGES FROM SERVER:" -ForegroundColor Cyan
            Write-Host "="*80
            foreach ($msg in $messagesResponse.messages) {
                $color = switch ($msg.type) {
                    "esriJobMessageTypeInformative" { "White" }
                    "esriJobMessageTypeWarning" { "Yellow" }
                    "esriJobMessageTypeError" { "Red" }
                    default { "Gray" }
                }
                Write-Host "[$($msg.type)] $($msg.description)" -ForegroundColor $color
            }
            Write-Host "="*80
        } else {
            Write-Host "  No messages available from server endpoint." -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  Could not retrieve messages from endpoint: $_" -ForegroundColor Yellow
    }
    
    # Try Method 2: Log File
    Write-Host "`nMethod 2: Checking Log File..."
    try {
        $logDate = Get-Date -Format "yyyyMMdd"
        $logFile = "$LogPath\${logDate}_GenerateInfrataggingSummaryIslandWide.log"
        
        if (Test-Path $logFile) {
            Write-Host "`n📄 LOG FILE SUMMARY:" -ForegroundColor Cyan
            Write-Host "="*80
            Write-Host "Log File: $logFile"
            Write-Host "="*80
            
            # Read last 40 lines to capture summary
            $logLines = Get-Content $logFile -Tail 40
            
            # Find and display summary section
            $inSummary = $false
            $summaryLines = @()
            
            foreach ($line in $logLines) {
                # Start capturing at FINAL SUMMARY
                if ($line -match "FINAL SUMMARY|JOB COMPLETED SUCCESSFULLY") {
                    $inSummary = $true
                }
                
                if ($inSummary) {
                    $summaryLines += $line
                }
            }
            
            if ($summaryLines.Count -gt 0) {
                foreach ($line in $summaryLines) {
                    # Highlight key metrics
                    if ($line -match "Depending Features Processed|Supporting Features Processed|Total Records") {
                        Write-Host $line -ForegroundColor Green
                    } else {
                        Write-Host $line
                    }
                }
            } else {
                Write-Host "No summary found in log. Showing last 20 lines:"
                Write-Host "="*80
                Get-Content $logFile -Tail 20
            }
            
            Write-Host "="*80
            Write-Host "`n✓ Full log available at: $logFile" -ForegroundColor Green
            
        } else {
            Write-Host "  Log file not found at: $logFile" -ForegroundColor Yellow
            Write-Host "  Checking if log folder exists..."
            if (Test-Path $LogPath) {
                Write-Host "  Log folder exists. Listing recent log files:"
                Get-ChildItem $LogPath -Filter "*GenerateInfrataggingSummaryIslandWide*.log" | 
                    Sort-Object LastWriteTime -Descending | 
                    Select-Object -First 5 | 
                    ForEach-Object { Write-Host "    $($_.Name) - $($_.LastWriteTime)" }
            } else {
                Write-Host "  Log folder does not exist: $LogPath" -ForegroundColor Red
            }
        }
    } catch {
        Write-Host "  Error reading log file: $_" -ForegroundColor Red
    }
    
    # Try Method 3: Check Results Parameters
    Write-Host "`nMethod 3: Checking Result Parameters..."
    try {
        if ($statusResponse.results) {
            Write-Host "`n📊 RESULT PARAMETERS:" -ForegroundColor Cyan
            Write-Host "="*80
            $statusResponse.results | ConvertTo-Json -Depth 10
            Write-Host "="*80
        } else {
            Write-Host "  No result parameters defined." -ForegroundColor Gray
        }
    } catch {
        Write-Host "  Could not retrieve result parameters." -ForegroundColor Yellow
    }
    
    # ============================================================================
    # STEP 5: VERIFY DATABASE (OPTIONAL)
    # ============================================================================
    
    Write-Host "`n" + "="*80 -ForegroundColor Green
    Write-Host "✓ JOB VERIFICATION COMPLETE" -ForegroundColor Green
    Write-Host "="*80 -ForegroundColor Green
    Write-Host "`nTo verify data was inserted, run this SQL query:" -ForegroundColor Cyan
    Write-Host @"
SELECT 
    COUNT(*) as Total_Records,
    MAX(UPDATEDDATE) as Last_Update,
    SUM(CASE WHEN CATEGORY = 0 THEN 1 ELSE 0 END) as No_Issues,
    SUM(CASE WHEN CATEGORY = 1 THEN 1 ELSE 0 END) as Has_Issues
FROM ONETOOLAPP.INFRATAGGING_SUMMARY_CACHE
"@ -ForegroundColor White
    
    exit 0
    
} elseif ($jobStatus -eq "esriJobFailed") {
    Write-Host "`n" + "="*80 -ForegroundColor Red
    Write-Host "✗ JOB FAILED!" -ForegroundColor Red
    Write-Host "="*80 -ForegroundColor Red
    
    # Try to get error messages
    Write-Host "`nAttempting to retrieve error messages..."
    try {
        $messagesUrl = "$baseUrl/jobs/$jobId/messages?f=json"
        $messagesResponse = Invoke-RestMethod -Uri $messagesUrl -Method POST
        
        if ($messagesResponse.messages -and $messagesResponse.messages.Count -gt 0) {
            Write-Host "`n❌ ERROR MESSAGES:" -ForegroundColor Red
            Write-Host "="*80
            foreach ($msg in $messagesResponse.messages) {
                Write-Host "[$($msg.type)] $($msg.description)" -ForegroundColor Red
            }
            Write-Host "="*80
        }
    } catch {
        Write-Host "Could not retrieve error messages: $_" -ForegroundColor Red
    }
    
    # Check log file for errors
    Write-Host "`nChecking log file for errors..."
    try {
        $logDate = Get-Date -Format "yyyyMMdd"
        $logFile = "$LogPath\${logDate}_GenerateInfrataggingSummaryIslandWide.log"
        
        if (Test-Path $logFile) {
            Write-Host "`nLast 30 lines of log file:"
            Write-Host "="*80
            Get-Content $logFile -Tail 30
            Write-Host "="*80
        }
    } catch {
        Write-Host "Could not read log file: $_" -ForegroundColor Red
    }
    
    exit 1
    
} else {
    Write-Host "`n" + "="*80 -ForegroundColor Yellow
    Write-Host "⚠ JOB TIMEOUT - Status: $jobStatus" -ForegroundColor Yellow
    Write-Host "="*80 -ForegroundColor Yellow
    Write-Host "Job did not complete within the expected time." -ForegroundColor Yellow
    Write-Host "Job ID: $jobId" -ForegroundColor Yellow
    Write-Host "Check ArcGIS Server Manager for job status." -ForegroundColor Yellow
    
    exit 2
}
