# ⚡ Quick Start - Update Your Jenkins Script

## **🎯 What You Need to Do (3 Steps)**

### **Step 1: Download the Updated Script**
File location: `/workspace/jenkins_updated_script.ps1`

---

### **Step 2: Update Configuration (Line 8)**

**Find this line:**
```powershell
$logPath = "Y:\logfiles\GPLogs"
```

**Update to match your Python script's LOG_FOLDER:**

Check your Python script (line 28):
```python
LOG_FOLDER = r"Y:\logfiles\GPLogs"  # or r"C:\temp\GPLogs"
```

If your Python uses `C:\temp\GPLogs`, change PowerShell to:
```powershell
$logPath = "C:\temp\GPLogs"
```

**⚠️ IMPORTANT:** These MUST match exactly!

---

### **Step 3: Replace Your Jenkins Script**

**Current Jenkins Script Location:**
```
Your Jenkins workspace → OneTool EXT DEV Scheduler → PowerShell script
```

**Actions:**
1. Open your Jenkins job configuration
2. Find the "Execute Windows batch command" or "Execute PowerShell script" section
3. Replace the entire script content with `jenkins_updated_script.ps1`
4. Save

---

## **✅ Verification (After Next Job Run)**

### **You Should See:**
```
================================================================================
✓ JOB COMPLETED SUCCESSFULLY!
================================================================================

📊 JOB SUMMARY:
================================================================================
  - Depending Features Processed: 452
  - Supporting Features Processed: 346
  - Total Records Inserted: 798
================================================================================
```

### **If You See:**
```
⚠ Summary file not found
```

**Fix:**
- Check `$logPath` in PowerShell matches `LOG_FOLDER` in Python
- Verify folder exists and has write permissions
- Check log file was actually created

---

## **🔍 Quick Test (Before Job Runs)**

Run this in PowerShell to verify configuration:

```powershell
# Test 1: Check folder exists
$logPath = "Y:\logfiles\GPLogs"  # Your configured path
Test-Path $logPath
# Should return: True

# Test 2: Check if you can read from folder
Get-ChildItem $logPath | Select-Object -First 5
# Should list files (if any exist)
```

---

## **📋 Files Reference**

| Need | File |
|------|------|
| **Implementation** | `jenkins_updated_script.ps1` |
| **What changed** | `JENKINS_SCRIPT_CHANGES.md` |
| **Complete guide** | `COMPLETE_SOLUTION_SUMMARY.md` |
| **Quick fix only** | `QUICK_FIX_GUIDE.md` |

---

## **💡 That's It!**

After these 3 steps, your next Jenkins job run will show the complete summary with record counts.

**Current behavior:**
```
Job completed successfully!
Job Messages:
[Empty]
```

**New behavior:**
```
✓ JOB COMPLETED SUCCESSFULLY!

📊 JOB SUMMARY:
  - Depending Features Processed: 452
  - Supporting Features Processed: 346
  - Total Records Inserted: 798
```

🎉 **Ready to go!**
