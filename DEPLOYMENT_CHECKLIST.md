# Deployment Checklist

## Pre-Deployment (Complete Before Making Changes)

### Backup
- [ ] Backup current GP service script
- [ ] Note current Jenkins job ID for comparison
- [ ] Document current behavior (for rollback reference)
- [ ] Save ArcGIS Server service configuration

### Verification
- [ ] Verify ArcGIS Server Python version: `python --version`
- [ ] Check current encoding: `python -c "import sys; print(sys.stdout.encoding)"`
- [ ] Verify LOG_FOLDER exists: `Test-Path "C:\Logs\InfraTagging"`
- [ ] Verify LOG_FOLDER is writable by ArcGIS service account
- [ ] Test database connectivity from ArcGIS Server

### Configuration Review
- [ ] Copy `generate_infratagging_summary.py` to local workstation
- [ ] Update `SDE_PATH` configuration
- [ ] Update `APP_SCHEMA` configuration (keep trailing dot)
- [ ] Update `LOG_FOLDER` configuration
- [ ] Verify `LOG_LEVEL` setting (default: INFO)
- [ ] Save configured script

---

## Deployment (Execute These Steps)

### Step 1: Service Preparation
- [ ] Login to ArcGIS Server Manager
- [ ] Navigate to Services
- [ ] Find GP service: `GenerateInfrataggingSummaryIslandWide`
- [ ] Note current service status
- [ ] Stop the GP service

### Step 2: Script Replacement
- [ ] Connect to ArcGIS Server file system
- [ ] Navigate to GP service script location
- [ ] Rename current script to: `[original_name]_backup_[date].py`
- [ ] Copy new `generate_infratagging_summary.py` to service location
- [ ] Verify file permissions (should match original)
- [ ] Verify file size (should be similar to original)

### Step 3: Service Restart
- [ ] Return to ArcGIS Server Manager
- [ ] Start the GP service
- [ ] Wait 30 seconds for service initialization
- [ ] Verify service status shows "Started"
- [ ] Check ArcGIS Server logs for any startup errors

---

## Testing (Verify Everything Works)

### Smoke Test (Quick Verification)
- [ ] Open ArcGIS Server Manager
- [ ] Navigate to the GP service
- [ ] Click "View Service"
- [ ] Verify service description loads
- [ ] Check no errors in service page

### Manual Test (Optional but Recommended)
- [ ] Navigate to service REST endpoint
- [ ] Submit a test job manually
- [ ] Monitor job status
- [ ] Verify job completes successfully
- [ ] Check log files are created
- [ ] Verify cache table updated

### Jenkins Test (Critical)
- [ ] Navigate to Jenkins job
- [ ] Click "Build Now"
- [ ] Monitor console output in real-time
- [ ] Verify no "force" error appears
- [ ] Verify no UnicodeEncodeError appears
- [ ] Wait for job completion
- [ ] Verify job status shows SUCCESS
- [ ] Check build history shows green checkmark

---

## Post-Deployment Verification

### Log File Verification
- [ ] Navigate to LOG_FOLDER
- [ ] Find today's log file: `[YYYYMMDD]_GenerateInfrataggingSummaryIslandWide.log`
- [ ] Open log file
- [ ] Verify no error messages
- [ ] Check timestamps are recent
- [ ] Verify expected log entries present

### Summary File Verification  
- [ ] In LOG_FOLDER, find: `[YYYYMMDD]_Summary.txt`
- [ ] Open summary file
- [ ] Verify shows: `[SUCCESS] JOB COMPLETED SUCCESSFULLY!`
- [ ] Check record counts match expectations
- [ ] Verify no Unicode encoding issues in file

### Database Verification
- [ ] Connect to database
- [ ] Query cache table: `SELECT COUNT(*) FROM INFRATAGGING_SUMMARY_CACHE`
- [ ] Verify record count matches summary file
- [ ] Check UPDATEDDATE matches execution time
- [ ] Verify both TYPE values present (0 and 1)
- [ ] Sample a few records to verify CHARTJSON populated

### Jenkins Output Verification
Review Jenkins console output for:
- [ ] No "Error setting up logging" messages
- [ ] No "UnicodeEncodeError" messages
- [ ] Shows "Processing Depending Features..."
- [ ] Shows "Processing Supporting Features..."
- [ ] Shows "Updating Infratagging Cache table..."
- [ ] Shows "[SUCCESS] INSERTION COMPLETED SUCCESSFULLY"
- [ ] Shows "[SUCCESS] JOB COMPLETED SUCCESSFULLY!"
- [ ] Shows correct record counts in FINAL SUMMARY
- [ ] Build status: SUCCESS (green)

---

## Issue Resolution

### If Jenkins Shows FAILURE

**Check 1: Review Error Messages**
- [ ] Look for specific error in Jenkins console
- [ ] Note the exact error message
- [ ] Check line number if provided

**Check 2: Review ArcGIS Server Logs**
- [ ] Navigate to: `C:\arcgisserver\logs\`
- [ ] Find logs for service execution time
- [ ] Look for Python exceptions
- [ ] Check for encoding errors

**Check 3: Review Script Logs**
- [ ] Open log file in LOG_FOLDER
- [ ] Find ERROR level messages
- [ ] Check for traceback
- [ ] Identify failing method

**Check 4: Common Issues**

| Error Message | Likely Cause | Solution |
|---------------|--------------|----------|
| "Error setting up logging: Unrecognised argument(s): force" | Old version deployed | Verify new script deployed correctly |
| UnicodeEncodeError | Unicode character still present | Search for Unicode chars in script |
| "Table does not exist" | Configuration incorrect | Verify APP_SCHEMA value |
| "Cannot open log file" | Permission issue | Check LOG_FOLDER permissions |
| "Connection failed" | Database issue | Test SDE connection |

---

## Rollback Procedure (If Needed)

### When to Rollback
Rollback if:
- [ ] Jenkins job fails 2+ times with same error
- [ ] Error cannot be quickly identified
- [ ] Production deadline approaching
- [ ] Database corruption suspected

### Rollback Steps
- [ ] Stop GP service in ArcGIS Server Manager
- [ ] Delete new script file
- [ ] Rename backup file to original name
- [ ] Verify file permissions correct
- [ ] Start GP service
- [ ] Test with Jenkins job
- [ ] Verify original behavior restored
- [ ] Document reason for rollback
- [ ] Schedule time to investigate and retry

---

## Success Criteria

All items must be checked for successful deployment:

### Critical (Must Pass)
- [x] Jenkins job completes without errors
- [x] Job status shows SUCCESS
- [x] No "force" error in logs
- [x] No UnicodeEncodeError in logs
- [x] Cache table populated with records
- [x] Record counts match expectations

### Important (Should Pass)
- [ ] Log files created successfully
- [ ] Summary file contains expected content
- [ ] Execution time similar to before
- [ ] No new warnings in logs
- [ ] Database performance acceptable

### Nice to Have
- [ ] Log messages more readable
- [ ] Summary format improved
- [ ] Error handling more robust

---

## Communication

### On Success
**Notify stakeholders:**
- [x] Deployment completed successfully
- [x] Jenkins job running cleanly
- [x] No errors observed
- [x] Next scheduled run: [time]

### On Failure
**Escalation:**
1. **Immediate:** Rollback to previous version
2. **Within 1 hour:** Document error details
3. **Within 4 hours:** Root cause analysis
4. **Within 1 day:** Fix and retry OR schedule maintenance window

---

## Sign-Off

**Deployed By:** ___________________________  
**Date/Time:** ___________________________  
**Jenkins Job ID:** ___________________________  
**Result:** ⬜ SUCCESS  ⬜ FAILURE  ⬜ ROLLBACK  

**Notes:**
_____________________________________________________________
_____________________________________________________________
_____________________________________________________________

**Verified By:** ___________________________  
**Date/Time:** ___________________________  

---

## Next Steps

After successful deployment:
- [ ] Monitor next 2-3 scheduled runs
- [ ] Review logs for any warnings
- [ ] Compare execution times
- [ ] Document any unexpected behavior
- [ ] Update runbook if needed
- [ ] Archive deployment documentation

---

## Contact Information

**Primary Contact:** [Your Name]  
**Email:** [your.email@company.com]  
**Phone:** [your phone]  

**Backup Contact:** [Backup Name]  
**Email:** [backup.email@company.com]  
**Phone:** [backup phone]  

**After Hours:** [On-call contact]

---

## Documentation References

- **Technical Details:** See `FIXES_APPLIED.md`
- **Deployment Guide:** See `README_DEPLOYMENT.md`
- **Change Summary:** See `CHANGES_SUMMARY.md`
- **This Checklist:** `DEPLOYMENT_CHECKLIST.md`

---

**Document Version:** 1.0  
**Last Updated:** 2025-12-01  
**Next Review:** After 10 successful runs
