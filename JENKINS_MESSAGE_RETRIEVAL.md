# 📨 ArcGIS Server Messages - Retrieval Guide

## **Issue Identified**

Your Jenkins log shows:
```json
{
    "jobId": "j9a58d9e777bb4279b30648125afaae98",
    "jobStatus": "esriJobSucceeded",
    "messages": []  ← Empty!
}
```

**The job succeeded but messages array is empty!**

---

## **Why This Happens**

ArcGIS Server GP services have a known behavior:
- ✅ Progress messages work (`arcpy.SetProgressorLabel`) - You saw these!
- ❌ Job messages might not persist in the final status response
- Messages might only be available during execution, not after completion

---

## **Solution: Check the Messages Endpoint Separately**

### **Option 1: Query Messages Endpoint Directly**

After the job completes, query:
```
https://3.gis.gov.sg/onetool/rest/services/ONETOOL_GPTOOLS/GenerateInfrataggingSummaryIslandWide/GPServer/GenerateInfrataggingSummaryIslandWide/jobs/{jobId}/messages?f=json
```

**PowerShell Example:**
```powershell
$jobId = "j9a58d9e777bb4279b30648125afaae98"
$messagesUrl = "https://3.gis.gov.sg/onetool/rest/services/ONETOOL_GPTOOLS/GenerateInfrataggingSummaryIslandWide/GPServer/GenerateInfrataggingSummaryIslandWide/jobs/$jobId/messages?f=json"

$messages = Invoke-RestMethod -Uri $messagesUrl -Method POST
Write-Host "Job Messages:"
$messages.messages | ForEach-Object {
    Write-Host "[$($_.type)] $($_.description)"
}
```

---

### **Option 2: Check the Log File**

The script writes to:
```
Y:\logfiles\GPLogs\YYYYMMDD_GenerateInfrataggingSummaryIslandWide.log
```

**PowerShell to Read Log:**
```powershell
$logDate = Get-Date -Format "yyyyMMdd"
$logFile = "Y:\logfiles\GPLogs\${logDate}_GenerateInfrataggingSummaryIslandWide.log"

if (Test-Path $logFile) {
    Write-Host "Log File Contents:"
    Get-Content $logFile -Tail 50  # Last 50 lines
}
```

**Look for:**
```
[2025-11-25 15:10:58] JOB COMPLETED SUCCESSFULLY!
[2025-11-25 15:10:58] FINAL SUMMARY:
[2025-11-25 15:10:58]   - Depending Features Processed: 452
[2025-11-25 15:10:58]   - Supporting Features Processed: 346
[2025-11-25 15:10:58]   - Total Records Inserted to Cache Table: 798
```

---

### **Option 3: Updated PowerShell Script for Jenkins**

Update your Jenkins PowerShell script to retrieve messages:

```powershell
# Your existing code to submit and poll job...
# After job completes:

if ($jobStatus -eq "esriJobSucceeded") {
    Write-Host "Job completed successfully!"
    
    # Try to get messages from messages endpoint
    try {
        $messagesUrl = "$baseUrl/jobs/$jobId/messages?f=json"
        $messagesResponse = Invoke-RestMethod -Uri $messagesUrl -Method POST -Body $tokenBody
        
        if ($messagesResponse.messages -and $messagesResponse.messages.Count -gt 0) {
            Write-Host "`nJob Messages:"
            foreach ($msg in $messagesResponse.messages) {
                Write-Host "  [$($msg.type)] $($msg.description)"
            }
        } else {
            Write-Host "`nNo messages in response. Checking log file..."
            
            # Fallback: Read from log file
            $logDate = Get-Date -Format "yyyyMMdd"
            $logFile = "Y:\logfiles\GPLogs\${logDate}_GenerateInfrataggingSummaryIslandWide.log"
            
            if (Test-Path $logFile) {
                Write-Host "`nLog File Summary (Last 20 lines):"
                Get-Content $logFile -Tail 20
            }
        }
    } catch {
        Write-Host "Could not retrieve messages: $_"
        Write-Host "Check log file: Y:\logfiles\GPLogs\${logDate}_GenerateInfrataggingSummaryIslandWide.log"
    }
}
```

---

## **Option 4: Verify Script is Actually Working**

Even though messages don't show, verify the job DID work:

### **Check 1: Database Records**
```sql
SELECT 
    COUNT(*) as Total_Records,
    MAX(UPDATEDDATE) as Last_Update
FROM ONETOOLAPP.INFRATAGGING_SUMMARY_CACHE
```

**If records were inserted today** → ✅ Script worked!

### **Check 2: Log File**
```
Y:\logfiles\GPLogs\20251125_GenerateInfrataggingSummaryIslandWide.log
```

**If file exists and has today's timestamp** → ✅ Script ran!

### **Check 3: Category Distribution**
```sql
SELECT 
    CATEGORY,
    COUNT(*) as Count,
    CASE WHEN CATEGORY = 0 THEN 'No Issues' ELSE 'Has Issues' END as Status
FROM ONETOOLAPP.INFRATAGGING_SUMMARY_CACHE
GROUP BY CATEGORY
```

**If you see both categories** → ✅ Issue detection worked!

---

## **Why Progress Messages Work But Final Messages Don't**

### **Progress Messages (✅ Working):**
```
"progress": {
    "type": "default",
    "message": "Processing Supporting Features..."
}
```
- Set by `arcpy.SetProgressorLabel()`
- Stored in job's progress property
- Persists during execution

### **Job Messages (❌ Empty):**
```
"messages": []
```
- Set by `arcpy.AddMessage()`
- Should contain execution details
- **Might be cleared when job completes**
- Or only available through separate endpoint

---

## **Recommended Solution**

### **Update Your Jenkins PowerShell Script:**

```powershell
# After job succeeds, check log file for summary
if ($jobStatus -eq "esriJobSucceeded") {
    Write-Host "✓ Job completed successfully!"
    
    # Read summary from log file
    $logDate = Get-Date -Format "yyyyMMdd"
    $logPath = "Y:\logfiles\GPLogs"
    $logFile = "$logPath\${logDate}_GenerateInfrataggingSummaryIslandWide.log"
    
    if (Test-Path $logFile) {
        Write-Host "`n" + "="*80
        Write-Host "JOB SUMMARY FROM LOG FILE:"
        Write-Host "="*80
        
        # Get last 30 lines (contains summary)
        $logLines = Get-Content $logFile -Tail 30
        
        # Extract summary section
        $inSummary = $false
        foreach ($line in $logLines) {
            if ($line -match "FINAL SUMMARY") {
                $inSummary = $true
            }
            if ($inSummary) {
                Write-Host $line
            }
        }
        
        Write-Host "="*80
        Write-Host "Full log: $logFile"
    } else {
        Write-Host "Warning: Log file not found at $logFile"
    }
    
    # Also check database
    Write-Host "`nVerifying database updates..."
    # Add SQL check here if needed
}
```

---

## **Alternative: Add Output Parameter to GP Tool**

If you want messages in the REST API response:

### **1. Modify Tool Properties (in ArcGIS Pro):**
- Add Output Parameter: `Output_Summary` (String, Output)

### **2. Script Will Set Output:**
```python
arcpy.SetParameterAsText(0, summary_msg)
```

### **3. REST API Response Will Include:**
```json
{
    "jobStatus": "esriJobSucceeded",
    "results": {
        "Output_Summary": {
            "paramUrl": "https://.../results/Output_Summary",
            "dataType": "GPString",
            "value": "FINAL SUMMARY: ... Total: 798"
        }
    }
}
```

---

## **Quick Verification Steps**

### **1. Check if script actually ran:**
```powershell
# Check log file exists
Test-Path "Y:\logfiles\GPLogs\$(Get-Date -Format 'yyyyMMdd')_GenerateInfrataggingSummaryIslandWide.log"
```

### **2. Check if data was inserted:**
```sql
SELECT TOP 1 UPDATEDDATE FROM ONETOOLAPP.INFRATAGGING_SUMMARY_CACHE ORDER BY UPDATEDDATE DESC
```

### **3. Get record count:**
```sql
SELECT COUNT(*) FROM ONETOOLAPP.INFRATAGGING_SUMMARY_CACHE
```

---

## **Summary**

| Method | Pros | Cons |
|--------|------|------|
| **Messages endpoint** | Detailed messages | Might be empty after completion |
| **Log file** | Always has complete details | Need file system access |
| **Output parameter** | In REST API response | Need to modify tool definition |
| **Database check** | Verifies actual work done | Doesn't show process details |
| **Progress messages** | Work during execution | Only show current step |

---

## **Recommended Approach**

**Use the log file!** It's the most reliable:

```powershell
# In your Jenkins PowerShell script, after job succeeds:
$logFile = "Y:\logfiles\GPLogs\$(Get-Date -Format 'yyyyMMdd')_GenerateInfrataggingSummaryIslandWide.log"
Get-Content $logFile -Tail 30 | Where-Object { $_ -match "FINAL SUMMARY|Total Records|Depending|Supporting" }
```

**This will show:**
```
[2025-11-25 15:10:58] FINAL SUMMARY:
[2025-11-25 15:10:58]   - Depending Features Processed: 452
[2025-11-25 15:10:58]   - Supporting Features Processed: 346
[2025-11-25 15:10:58]   - Total Records Inserted to Cache Table: 798
```

---

🎉 **The script IS working (jobStatus = esriJobSucceeded), but messages need to be retrieved from the log file or messages endpoint!**
