# Infrastructure Tagging Summary - Deployment Guide

## Quick Fix Summary

Your Jenkins job was failing due to two main issues:
1. **Python logging compatibility** - `force=True` not supported in older Python
2. **Unicode encoding errors** - Checkmark symbols `✓` couldn't be encoded in Windows cp1252

## Files in This Repository

- `generate_infratagging_summary.py` - **Fixed Python script (USE THIS)**
- `FIXES_APPLIED.md` - Detailed explanation of all fixes
- `README_DEPLOYMENT.md` - This deployment guide

## Deployment Steps

### Step 1: Backup Current Script
Before making changes, backup your current GP service script:
```bash
# Save a copy of your current working script
copy \\your\arcgis\server\path\current_script.py current_script_backup.py
```

### Step 2: Update Configuration
Edit the configuration section at the top of `generate_infratagging_summary.py`:

```python
# ========================================================================
# CONFIGURATION - Update these values for your environment
# ========================================================================
SDE_PATH = arcpy.GetParameterAsText(0) if arcpy.GetParameterAsText(0) else r"Database Connections\YourConnection.sde"
APP_SCHEMA = "YOUR_SCHEMA."  # Update with your schema name
LOG_FOLDER = r"C:\Logs\InfraTagging"  # Update with your log folder path
LOG_LEVEL = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR
```

Update:
- `SDE_PATH` - Your database connection path
- `APP_SCHEMA` - Your database schema name (keep the trailing dot)
- `LOG_FOLDER` - Where you want log files saved
- `LOG_LEVEL` - Logging verbosity level

### Step 3: Replace Script in ArcGIS Server
1. Copy the fixed `generate_infratagging_summary.py` to your ArcGIS Server scripts directory
2. Ensure the file has the same name as your current GP tool script
3. Verify file permissions allow ArcGIS Server to read the file

### Step 4: Republish GP Service (if needed)
If your ArcGIS Server caches the script:
1. Open ArcGIS Server Manager
2. Stop the GP service
3. Start the GP service
4. Test the service manually first

### Step 5: Test with Jenkins
Run your Jenkins job and verify:
- [ ] Job completes successfully
- [ ] No "Unrecognised argument(s): force" error
- [ ] No UnicodeEncodeError
- [ ] Jenkins shows "SUCCESS" status
- [ ] Log files are created correctly
- [ ] Summary file is generated

## Expected Jenkins Output (Success)

```
Job successfully submitted. Job ID: je71cde966a094a108f719d6fccb07a55
Polling job status using POST method...
Current Job Status: esriJobSubmitted
Current Job Status: esriJobExecuting
Progress: Processing Depending Features...
Progress: Processing Supporting Features...
Progress: Updating Infratagging Cache table...
Current Job Status: esriJobSucceeded

Messages:
  [SUCCESS] INSERTION COMPLETED SUCCESSFULLY
  [SUCCESS] JOB COMPLETED SUCCESSFULLY!
  
FINAL SUMMARY:
  - Depending Features Processed: XXX
  - Supporting Features Processed: XXX
  - Total Records Inserted to Cache Table: XXX

Build Status: SUCCESS
```

## What Changed (Quick Reference)

| Old Code | New Code | Reason |
|----------|----------|--------|
| `force=True` in logging.basicConfig | Manual handler removal loop | Python 3.7 compatibility |
| `✓` checkmark | `[SUCCESS]` | ASCII-safe encoding |
| `✗` cross | `[FAILED]` | ASCII-safe encoding |
| `\u21B5` arrow | `->` | ASCII-safe encoding |
| `open(file, 'w')` | `open(file, 'w', encoding='utf-8')` | Explicit UTF-8 encoding |

## Troubleshooting

### If Jenkins still fails:

1. **Check Python version on ArcGIS Server:**
   ```python
   import sys
   print(sys.version)
   ```

2. **Check encoding in ArcGIS Server environment:**
   ```python
   import sys
   print(sys.stdout.encoding)
   ```

3. **Verify log folder exists and has write permissions:**
   ```python
   import os
   print(os.path.exists(LOG_FOLDER))
   print(os.access(LOG_FOLDER, os.W_OK))
   ```

4. **Check ArcGIS Server logs:**
   - Location: `C:\arcgisserver\logs\`
   - Look for Python exceptions or encoding errors

### Common Issues:

**Issue:** Script still has Unicode errors
**Solution:** Search for any remaining Unicode characters (✓, ✗, arrows, etc.) and replace with ASCII

**Issue:** Logging still fails
**Solution:** Verify LOG_FOLDER exists and ArcGIS Server service account has write permissions

**Issue:** Jenkins shows "Failed" but script works manually
**Solution:** Check that output messages don't contain any Unicode characters

## Verification Commands

After deployment, verify in ArcGIS Server Python environment:

```python
# Test 1: Verify no Unicode in messages
test_msg = "[SUCCESS] INSERTION COMPLETED SUCCESSFULLY"
print(test_msg.encode('ascii'))  # Should not raise exception

# Test 2: Verify logging works
import logging
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(filename='test.log', level=logging.INFO)
logging.info("Test message")  # Should create test.log

# Test 3: Verify file encoding
with open('test.txt', 'w', encoding='utf-8') as f:
    f.write("[SUCCESS] Test\n")
```

## Support

If issues persist after deployment:
1. Check the detailed error logs in Jenkins output
2. Review ArcGIS Server logs
3. Verify configuration values are correct
4. Ensure database connectivity from ArcGIS Server
5. Test the GP service manually through ArcGIS Server Manager

## Rollback Plan

If the new script causes issues:
1. Stop the GP service
2. Restore the backup script
3. Restart the GP service
4. Contact support with error details from Jenkins and ArcGIS Server logs
