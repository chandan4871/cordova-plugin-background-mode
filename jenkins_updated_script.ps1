# ================================================================================
# Jenkins PowerShell Script - Updated with Summary File Reading
# ================================================================================

# Configuration
$logPath = "Y:\logfiles\GPLogs"  # Update if different
# If using C:\temp\GPLogs, change to: $logPath = "C:\temp\GPLogs"

# Submitting the job to ArcGIS server, requesting JSON response with f=json
Write-Host "Submitting the job to ArcGIS server..."
$response = Invoke-RestMethod -Method Post `
    -Uri "https://3.gis.gov.sg/onetool/rest/services/ONETOOL_GPTOOLS/GenerateInfrataggingSummaryIslandWide/GPServer/GenerateInfrataggingSummaryIslandWide/submitJob?f=json" `
    -UseBasicParsing

# Convert the response to a string for easier handling
$responseString = $response | Out-String
Write-Host "Full Response: $responseString"  # Debugging: Print the full response

# Step 1: Check if the response is HTML (indicating an error, such as redirect to login page)
if ($responseString -match "<html") {
    Write-Host "Error: Received an HTML response, possibly a login page. Response was:"
    Write-Host $responseString
    exit 1
}

# Step 2: Extract the Job ID from the JSON response and ensure it's a string
try {
    $jobId = $response.jobId.ToString()  # Convert jobId to string explicitly
    Write-Host "Job successfully submitted. Job ID: $jobId"
} catch {
    Write-Host "Error: Unable to extract Job ID from the response. Response was:"
    Write-Host ($response | ConvertTo-Json -Depth 10)  # Debugging: Log the full JSON response
    exit 1
}

# Build the URL for polling the job status using manual concatenation
$jobStatusUrl = "https://3.gis.gov.sg/onetool/rest/services/ONETOOL_GPTOOLS/GenerateInfrataggingSummaryIslandWide/GPServer/GenerateInfrataggingSummaryIslandWide/jobs/" + $jobId + "?f=json"

# Print the full URL to ensure it's correct
Write-Host "Polling job status using POST method. Full URL: $jobStatusUrl"

# Step 3: Poll the job status using POST method until the job is complete (esriJobSucceeded or esriJobFailed)
$status = "esriJobSubmitted"
while ($status -eq "esriJobSubmitted" -or $status -eq "esriJobExecuting") {
    Write-Host "Polling job status using POST method..."

    # Poll the job details URL for status using POST method
    try {
        $statusResponse = Invoke-RestMethod -Method Post `
            -Uri $jobStatusUrl `
            -UseBasicParsing

        # Log the entire status response for debugging
        Write-Host "Full Status Response:"
        Write-Host ($statusResponse | ConvertTo-Json -Depth 10)

        # Extract the job status from the JSON response
        $status = $statusResponse.jobStatus
        Write-Host "Current Job Status: $status"
        
        # Show progress if available
        if ($statusResponse.progress) {
            Write-Host "Progress: $($statusResponse.progress.message)" -ForegroundColor Cyan
        }
    } catch {
        Write-Host "Error during status request or parsing response:"
        Write-Host $_
        exit 1
    }

    # Wait for 10 seconds before polling again
    Start-Sleep -Seconds 10
}

# ================================================================================
# Step 4: Check if the job succeeded or failed
# ================================================================================
if ($status -eq "esriJobSucceeded") {
    Write-Host "`n" + "="*80 -ForegroundColor Green
    Write-Host "✓ JOB COMPLETED SUCCESSFULLY!" -ForegroundColor Green
    Write-Host "="*80 -ForegroundColor Green
    
    # ============================================================================
    # NEW: Read Summary from Summary File (Primary Method)
    # ============================================================================
    $logDate = Get-Date -Format "yyyyMMdd"
    $summaryFile = "$logPath\${logDate}_Summary.txt"
    
    Write-Host "`nAttempting to read summary file: $summaryFile" -ForegroundColor Gray
    
    if (Test-Path $summaryFile) {
        Write-Host "`n📊 JOB SUMMARY:" -ForegroundColor Cyan
        Write-Host "="*80
        
        # Read and display the summary file
        Get-Content $summaryFile | ForEach-Object {
            # Highlight key metrics
            if ($_ -match "Depending Features|Supporting Features|Total Records") {
                Write-Host $_ -ForegroundColor Green
            } else {
                Write-Host $_
            }
        }
        
        Write-Host "="*80
        Write-Host "`n✓ Summary file location: $summaryFile" -ForegroundColor Gray
        
    } else {
        Write-Host "⚠ Summary file not found at: $summaryFile" -ForegroundColor Yellow
        Write-Host "Attempting to read from main log file..." -ForegroundColor Yellow
        
        # ========================================================================
        # FALLBACK: Read from Main Log File
        # ========================================================================
        $logFile = "$logPath\${logDate}_GenerateInfrataggingSummaryIslandWide.log"
        
        if (Test-Path $logFile) {
            Write-Host "`n📄 LOG FILE SUMMARY:" -ForegroundColor Cyan
            Write-Host "="*80
            
            # Get last 40 lines and extract summary
            $logLines = Get-Content $logFile -Tail 40
            
            # Find and display summary section
            $inSummary = $false
            $foundSummary = $false
            
            foreach ($line in $logLines) {
                # Start capturing at FINAL SUMMARY or JOB COMPLETED
                if ($line -match "FINAL SUMMARY|JOB COMPLETED SUCCESSFULLY") {
                    $inSummary = $true
                    $foundSummary = $true
                }
                
                if ($inSummary) {
                    # Highlight key metrics
                    if ($line -match "Depending Features|Supporting Features|Total Records") {
                        Write-Host $line -ForegroundColor Green
                    } else {
                        Write-Host $line
                    }
                }
            }
            
            if (-not $foundSummary) {
                Write-Host "⚠ No summary section found in log. Showing last 20 lines:" -ForegroundColor Yellow
                Write-Host "-"*80
                Get-Content $logFile -Tail 20
            }
            
            Write-Host "="*80
            Write-Host "Full log file: $logFile" -ForegroundColor Gray
            
        } else {
            Write-Host "❌ ERROR: Neither summary file nor log file found!" -ForegroundColor Red
            Write-Host "Expected locations:" -ForegroundColor Yellow
            Write-Host "  Summary: $summaryFile" -ForegroundColor Yellow
            Write-Host "  Log:     $logFile" -ForegroundColor Yellow
            Write-Host "`nPossible issues:" -ForegroundColor Yellow
            Write-Host "  1. Log folder path is incorrect (check LOG_FOLDER in Python script)" -ForegroundColor Yellow
            Write-Host "  2. Python script did not execute properly" -ForegroundColor Yellow
            Write-Host "  3. File permissions prevent file creation" -ForegroundColor Yellow
        }
    }
    
    # ============================================================================
    # Also Check REST API Messages (Usually Empty)
    # ============================================================================
    Write-Host "`n📨 REST API Messages:" -ForegroundColor Cyan
    if ($statusResponse.messages -and $statusResponse.messages.Count -gt 0) {
        Write-Host "Job Messages:"
        foreach ($message in $statusResponse.messages) {
            Write-Host "  $($message.type): $($message.description)"
        }
    } else {
        Write-Host "  (No messages in REST API response - This is expected)" -ForegroundColor Gray
    }
    
    # ============================================================================
    # Provide Database Verification SQL
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
    Write-Host "Finished: SUCCESS" -ForegroundColor Green
    Write-Host "="*80 -ForegroundColor Green
    
    exit 0
    
} else {
    # ============================================================================
    # Job Failed
    # ============================================================================
    Write-Host "`n" + "="*80 -ForegroundColor Red
    Write-Host "✗ JOB FAILED!" -ForegroundColor Red
    Write-Host "="*80 -ForegroundColor Red
    Write-Host "Job failed with status: $status" -ForegroundColor Red
    
    # Try to get error details from summary file
    $logDate = Get-Date -Format "yyyyMMdd"
    $summaryFile = "$logPath\${logDate}_Summary.txt"
    
    if (Test-Path $summaryFile) {
        Write-Host "`n❌ ERROR SUMMARY:" -ForegroundColor Red
        Write-Host "="*80
        Get-Content $summaryFile
        Write-Host "="*80
    } else {
        # Try log file
        $logFile = "$logPath\${logDate}_GenerateInfrataggingSummaryIslandWide.log"
        
        if (Test-Path $logFile) {
            Write-Host "`n❌ ERROR DETAILS FROM LOG (Last 30 lines):" -ForegroundColor Red
            Write-Host "="*80
            Get-Content $logFile -Tail 30
            Write-Host "="*80
        } else {
            Write-Host "❌ ERROR: Could not find log files to retrieve error details" -ForegroundColor Red
        }
    }
    
    # Check REST API messages
    if ($statusResponse.messages -and $statusResponse.messages.Count -gt 0) {
        Write-Host "`n📨 Error Messages from REST API:" -ForegroundColor Red
        foreach ($message in $statusResponse.messages) {
            Write-Host "  $($message.type): $($message.description)" -ForegroundColor Red
        }
    }
    
    Write-Host "`n" + "="*80 -ForegroundColor Red
    Write-Host "Finished: FAILURE" -ForegroundColor Red
    Write-Host "="*80 -ForegroundColor Red
    
    exit 1
}
