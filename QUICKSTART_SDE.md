# Quick Start Guide - Infrastructure Tagging GP Tool (SDE Version)

Get up and running in 3 minutes with SDE connections!

## What's Different in SDE Version?

✅ **No additional packages needed** - Uses only arcpy  
✅ **No pyodbc installation** - Works with SDE connections  
✅ **Native ArcGIS** - Uses enterprise geodatabase connections  

---

## Step 1: Create SDE Connection File (1 minute)

### In ArcGIS Pro:

1. **Catalog Pane** → **Databases**
2. Right-click → **New Database Connection**
3. Fill in:
   - **Database Platform**: SQL Server
   - **Instance**: YOUR_SQL_SERVER
   - **Authentication Type**: 
     - **Operating system authentication** (Windows Auth) ✅ Recommended
     - **Database authentication** (SQL Auth)
   - **Database**: YOUR_DATABASE
4. Click **Test Connection** (should succeed)
5. **Save** as: `ONETOOLDEV_ONETOOL_ARCGIS_CONN_SQL.sde`

💡 **Tip**: Check "Save user name and password" if using database authentication

---

## Step 2: Configure Settings (30 seconds)

Create `config_sde.json`:

```json
{
  "database": {
    "sde_path": "C:\\temp\\SDE_Conn\\ONETOOLDEV_ONETOOL_ARCGIS_CONN_SQL.sde",
    "app_schema": "ONETOOLAPP."
  },
  "logging": {
    "log_folder": "C:\\temp\\GPLogs"
  }
}
```

**Replace:**
- `sde_path` with your actual .sde file path
- `app_schema` with your schema name (⚠️ include the trailing dot!)

---

## Step 3: Run (30 seconds)

### Option A: Using Python Directly

```bash
python run_infratagging_job_sde.py --config config_sde.json
```

### Option B: Using Batch File (Windows)

```batch
run_job_sde.bat
```

### Option C: Using Shell Script (Linux)

```bash
./run_job_sde.sh
```

### Option D: From ArcGIS Pro

1. **Catalog** → **Toolboxes** → **Add Toolbox**
2. Select: `InfraTaggingTools_SDE.pyt`
3. Double-click: **Generate Infratagging Summary Island Wide**
4. Fill in:
   - **SDE Connection File**: Browse to your .sde file
   - **Schema Name**: ONETOOLAPP.
   - **Log Folder**: C:\temp\GPLogs
5. Click **Run**

---

## Common SDE Connection Paths

### Windows
```
C:\Users\YOUR_USERNAME\AppData\Roaming\ESRI\ArcGISPro\Favorites\your_connection.sde
C:\ProgramData\ESRI\connections\your_connection.sde
C:\temp\SDE_Conn\your_connection.sde
```

### Linux
```
/home/username/.config/ESRI/connections/your_connection.sde
/opt/connections/your_connection.sde
```

---

## Schema Name Format

⚠️ **IMPORTANT**: Always include the trailing dot!

✅ **Correct**: `"ONETOOLAPP."`  
❌ **Wrong**: `"ONETOOLAPP"`

The script uses this in SQL queries like:
```sql
SELECT * FROM ONETOOLAPP.INFRATAGGING_MAPPING
```

---

## Verify It's Working

### Check Logs

```bash
# View log file (Windows)
type C:\temp\GPLogs\YYYYMMDD_InfraTaggingSummary.log

# View log file (Linux)
cat /var/log/infratagging/YYYYMMDD_InfraTaggingSummary.log
```

### Check Database

```sql
-- See latest records
SELECT TOP 10 *
FROM ONETOOLAPP.INFRATAGGING_SUMMARY_CACHE
ORDER BY CREATED_DATE DESC;

-- Count by type
SELECT 
    CASE WHEN TYPE = 0 THEN 'Depending' ELSE 'Supporting' END AS TYPE_NAME,
    COUNT(*) AS COUNT
FROM ONETOOLAPP.INFRATAGGING_SUMMARY_CACHE
GROUP BY TYPE;
```

---

## Troubleshooting

### ❌ "Module 'arcpy' not found"

**Solution**: Run from ArcGIS Python Command Prompt

```bash
# Windows: Open "Python Command Prompt" from ArcGIS Pro
# Or activate environment:
conda activate arcgispro-py3
```

### ❌ "Failed to connect to database"

**Solution**: Test your SDE connection

1. Open ArcGIS Pro
2. Catalog → Databases
3. Double-click your .sde file
4. Should see list of tables
5. If not, recreate the connection

### ❌ "Table does not exist"

**Solution**: Check schema name

1. Verify schema: `ONETOOLAPP.` (with dot!)
2. Check tables exist:
   ```sql
   SELECT TABLE_NAME 
   FROM INFORMATION_SCHEMA.TABLES 
   WHERE TABLE_SCHEMA = 'ONETOOLAPP'
   ```

### ❌ "Permission denied"

**Solution**: Verify database permissions

Test in SQL Server Management Studio:
```sql
-- Test read
SELECT * FROM ONETOOLAPP.INFRATAGGING_LAYERS_VW

-- Test write
INSERT INTO ONETOOLAPP.INFRATAGGING_SUMMARY_CACHE 
(FEATUREID, LAYER_ID, LAYER_NAME, TYPE, CATEGORY, CREATED_DATE)
VALUES ('TEST', -1, 'TEST', 0, 0, GETDATE())

-- Clean up
DELETE FROM ONETOOLAPP.INFRATAGGING_SUMMARY_CACHE WHERE FEATUREID = 'TEST'
```

---

## Next Steps

### ✅ Enable Email Notifications

Edit `config_sde.json`:

```json
{
  "database": { ... },
  "logging": { ... },
  "email": {
    "enabled": true,
    "smtp_server": "smtp.office365.com",
    "smtp_port": 587,
    "from_email": "noreply@company.com",
    "to_emails": ["admin@company.com"],
    "username": "noreply@company.com",
    "password": "your_password"
  }
}
```

### ✅ Schedule Execution

**Windows Task Scheduler:**
1. Open Task Scheduler
2. Create Basic Task
3. Schedule: Daily at 2:00 AM
4. Action: Start program: `C:\path\to\run_job_sde.bat`

**Linux Cron:**
```bash
crontab -e
# Add: 0 2 * * * /path/to/run_job_sde.sh >> /var/log/infratagging.log 2>&1
```

### ✅ Publish as GP Service

1. Run successfully in ArcGIS Pro (Step 3, Option D)
2. **Geoprocessing History** → Right-click successful run
3. **Share As** → **Web Tool**
4. Configure and **Publish** to ArcGIS Server

---

## Quick Reference

| Need to... | File/Command |
|------------|-------------|
| **Run manually** | `python run_infratagging_job_sde.py --config config_sde.json` |
| **Run with batch file** | `run_job_sde.bat` |
| **Run in ArcGIS Pro** | Add toolbox: `InfraTaggingTools_SDE.pyt` |
| **Configure** | Edit: `config_sde.json` |
| **Check logs** | View: `C:\temp\GPLogs\YYYYMMDD_InfraTaggingSummary.log` |
| **Check results** | Query: `ONETOOLAPP.INFRATAGGING_SUMMARY_CACHE` |

---

## Need More Help?

📖 **Detailed Guide**: See `README_SDE_VERSION.md`  
📋 **Full Deployment**: See `INFRATAGGING_DEPLOYMENT.md`  
❓ **Troubleshooting**: Check log files first!

---

**You're all set!** 🚀

The SDE version is perfect for ArcGIS environments and requires **zero additional Python packages**!
