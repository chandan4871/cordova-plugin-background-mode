# Infrastructure Tagging Summary - Python GP Tool (SDE Version)

## Overview

This is the **SDE Connection version** of the Infrastructure Tagging Summary generation tool. It uses ArcGIS SDE connections (`arcpy.ArcSDESQLExecute`) instead of pyodbc for database connectivity.

## Key Differences from pyodbc Version

| Feature | pyodbc Version | SDE Version |
|---------|----------------|-------------|
| **Database Connection** | Direct SQL Server connection | SDE connection file (.sde) |
| **Dependencies** | Requires pyodbc package | Uses built-in arcpy only |
| **Connection String** | SQL Server connection string | Path to .sde file |
| **Authentication** | Windows/SQL Server Auth | Managed by SDE connection |
| **Suitable For** | Any Python environment | ArcGIS Pro/Server only |

## Why Use SDE Version?

✅ **No additional packages required** - Uses only arcpy (included with ArcGIS)
✅ **Managed credentials** - Authentication handled by SDE connection file
✅ **Enterprise geodatabase support** - Works with versioned/unversioned data
✅ **ArcGIS native** - Follows ArcGIS best practices
✅ **Easier deployment** - No pip install required on ArcGIS Server

## Files Included (SDE Version)

### Core Scripts
1. **generate_infratagging_summary_sde.py** - Main processing engine using SDE
2. **InfraTaggingTools_SDE.pyt** - ArcGIS Python Toolbox for SDE
3. **run_infratagging_job_sde.py** - Standalone runner for SDE

### Configuration
4. **config_sde_example.json** - Configuration template for SDE version

### Execution Scripts
5. **run_job_sde.bat** - Windows batch file for SDE version
6. **run_job_sde.sh** - Linux shell script for SDE version

### Documentation
7. **README_SDE_VERSION.md** - This file

## Prerequisites

### Software
- ArcGIS Pro 2.8+ or ArcGIS Server 10.8+
- Python 3.7+ (included with ArcGIS)
- **NO additional packages needed!**

### Database
- Enterprise geodatabase (SQL Server)
- SDE connection file (.sde) with proper permissions

### Required Tables/Views
```
INFRATAGGING_MAPPING
INFRATAGGING_MAPPING_SUPP_VW
INFRATAGGING_LAYERS_VW
INFRA_CONS_STAGINGYR_VW
INFRATAGGING_SUMMARY_CACHE
```

## Quick Start (3 Steps)

### Step 1: Create SDE Connection File

In ArcGIS Pro:
1. Catalog Pane → Databases
2. Right-click → New Database Connection
3. Configure connection:
   - Database Platform: SQL Server
   - Instance: YOUR_SQL_SERVER
   - Authentication Type: Database authentication or Operating system authentication
   - Database: YOUR_DATABASE
4. Test connection
5. Save as: `ONETOOLDEV_ONETOOL_ARCGIS_CONN_SQL.sde`

### Step 2: Configure Settings

Create `config_sde.json`:

```json
{
  "database": {
    "sde_path": "C:\\temp\\SDE_Conn\\ONETOOLDEV_ONETOOL_ARCGIS_CONN_SQL.sde",
    "app_schema": "ONETOOLAPP."
  },
  "logging": {
    "log_folder": "C:\\temp\\GPLogs"
  },
  "email": {
    "enabled": false
  }
}
```

### Step 3: Run the Job

```bash
# Using Python directly
python run_infratagging_job_sde.py --config config_sde.json

# OR using Windows batch file
run_job_sde.bat

# OR using Linux shell script
./run_job_sde.sh
```

## Configuration

### Minimal Configuration

```json
{
  "database": {
    "sde_path": "C:\\path\\to\\your_connection.sde",
    "app_schema": "ONETOOLAPP."
  }
}
```

### Full Configuration

```json
{
  "database": {
    "sde_path": "C:\\temp\\SDE_Conn\\ONETOOLDEV_ONETOOL_ARCGIS_CONN_SQL.sde",
    "app_schema": "ONETOOLAPP.",
    "mgr_schema": "ONETOOLMGR."
  },
  "logging": {
    "log_folder": "C:\\temp\\GPLogs",
    "level": "INFO"
  },
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

### Important: Schema Name Format

⚠️ **Always include the trailing dot!**

✅ Correct: `"ONETOOLAPP."`
❌ Wrong: `"ONETOOLAPP"`

The schema name must end with a dot for proper SQL query formatting.

## Usage Examples

### Example 1: Run with Configuration File

```bash
python run_infratagging_job_sde.py --config config_sde.json
```

### Example 2: Run with Command-Line Arguments

```bash
python run_infratagging_job_sde.py \
  --sde-path "C:\temp\SDE_Conn\ONETOOLDEV_ONETOOL_ARCGIS_CONN_SQL.sde" \
  --schema "ONETOOLAPP." \
  --log-folder "C:\temp\GPLogs"
```

### Example 3: Run from ArcGIS Pro

1. Open ArcGIS Pro
2. Catalog Pane → Toolboxes
3. Right-click → Add Toolbox
4. Select: `InfraTaggingTools_SDE.pyt`
5. Expand toolbox
6. Double-click: "Generate Infratagging Summary Island Wide"
7. Fill in parameters:
   - **SDE Connection File**: Browse to your .sde file
   - **Schema Name**: ONETOOLAPP.
   - **Log Folder**: C:\temp\GPLogs
8. Click **Run**

### Example 4: Publish as GP Service

1. Run the tool successfully in ArcGIS Pro (Example 3)
2. In Geoprocessing History, find the successful run
3. Right-click → Share As → Web Tool
4. Configure:
   - Name: GenerateInfrataggingSummary
   - Summary: Processes infrastructure tagging summaries
   - Execution Mode: **Asynchronous**
   - Maximum timeout: 3600 seconds
5. Click **Analyze** to check for issues
6. Click **Publish**

### Example 5: Schedule with Windows Task Scheduler

1. Edit `run_job_sde.bat`:
   ```batch
   SET PYTHON_EXE=C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
   SET CONFIG_FILE=%SCRIPT_DIR%config_sde.json
   ```

2. Open Task Scheduler
3. Create Basic Task:
   - Name: Infratagging Summary Generation
   - Trigger: Daily at 2:00 AM
   - Action: Start a program
   - Program: `C:\path\to\run_job_sde.bat`
   - Start in: `C:\path\to\`

4. Additional settings:
   - Run whether user is logged on or not
   - Run with highest privileges

### Example 6: Schedule with Linux Cron

1. Edit `run_job_sde.sh`:
   ```bash
   PYTHON_EXE="/opt/arcgis/server/framework/runtime/python/bin/python"
   CONFIG_FILE="${SCRIPT_DIR}/config_sde.json"
   ```

2. Make executable:
   ```bash
   chmod +x run_job_sde.sh
   ```

3. Edit crontab:
   ```bash
   crontab -e
   ```

4. Add cron job (runs daily at 2 AM):
   ```
   0 2 * * * /path/to/run_job_sde.sh >> /var/log/infratagging.log 2>&1
   ```

## How It Works

### 1. SDE Connection
```python
# Initialize SDE connection
db_conn = arcpy.ArcSDESQLExecute(sde_path)

# Execute SQL
result = db_conn.execute(sql_query)
```

### 2. Query Execution

The script uses `arcpy.ArcSDESQLExecute` to run SQL queries:

```python
def execute_sql(self, sql: str):
    sde = arcpy.ArcSDESQLExecute(self.sde_path)
    result = sde.execute(sql)
    return result
```

Results are returned as:
- `list` of tuples for SELECT queries
- `True` for successful INSERT/UPDATE/DELETE
- Error message string for failures

### 3. Processing Flow

```
1. Get Dependency Links (Depending)
   ↓
2. Get Dependency Links (Supporting)
   ↓
3. Get Layer Information
   ↓
4. Process Each Feature
   ↓
5. Filter Schedule Links
   ↓
6. Check for Conflicts
   ↓
7. Generate Chart JSON
   ↓
8. Save to Cache Table
   ↓
9. Send Email Notification (optional)
```

## SDE Connection File Setup

### Windows Authentication

1. In ArcGIS Pro:
   - Authentication Type: **Operating system authentication**
   - No username/password needed

2. Connection string (in .sde file):
   ```
   INSTANCE=sde:sqlserver:YOUR_SERVER
   DATABASE=YOUR_DATABASE
   AUTHENTICATION_MODE=OSA
   ```

### SQL Server Authentication

1. In ArcGIS Pro:
   - Authentication Type: **Database authentication**
   - Username: your_username
   - Password: your_password

2. Connection string (in .sde file):
   ```
   INSTANCE=sde:sqlserver:YOUR_SERVER
   DATABASE=YOUR_DATABASE
   USER=your_username
   PASSWORD=encrypted_password
   ```

### Store Password

⚠️ When creating the SDE connection, check **"Save user name and password"** to store credentials in the .sde file.

## Troubleshooting

### "Module 'arcpy' not found"

**Problem:** Python script can't find arcpy module

**Solution:**
```bash
# Run from ArcGIS Python Command Prompt
# Or activate ArcGIS Pro Python environment:
conda activate arcgispro-py3
```

### "Failed to connect to database"

**Problem:** SDE connection file is invalid or database is unreachable

**Solution:**
1. Test connection in ArcGIS Pro:
   - Catalog → Databases
   - Double-click your .sde file
   - Should see tables listed
2. If fails, recreate SDE connection
3. Check firewall rules
4. Verify SQL Server is running

### "Table does not exist"

**Problem:** Schema name is incorrect or tables don't exist

**Solution:**
1. Verify schema name format: `ONETOOLAPP.` (with trailing dot)
2. Check tables exist:
   ```sql
   SELECT * FROM INFORMATION_SCHEMA.TABLES 
   WHERE TABLE_SCHEMA = 'ONETOOLAPP'
   ```
3. Verify SDE connection has access to schema

### "Permission denied"

**Problem:** SDE connection doesn't have required permissions

**Solution:**
1. Verify read permissions on source tables:
   - INFRATAGGING_MAPPING
   - INFRATAGGING_MAPPING_SUPP_VW
   - INFRATAGGING_LAYERS_VW
   - INFRA_CONS_STAGINGYR_VW

2. Verify write permissions on cache table:
   - INFRATAGGING_SUMMARY_CACHE

3. Test with:
   ```sql
   SELECT * FROM ONETOOLAPP.INFRATAGGING_LAYERS_VW
   INSERT INTO ONETOOLAPP.INFRATAGGING_SUMMARY_CACHE (...) VALUES (...)
   ```

### "SQL execution failed"

**Problem:** SQL query has errors

**Solution:**
1. Check logs for SQL statement
2. Test SQL query in SQL Server Management Studio
3. Verify table/column names
4. Check data types

### "Log folder doesn't exist"

**Problem:** Specified log folder is invalid

**Solution:**
```bash
# Create log folder
mkdir C:\temp\GPLogs

# Or update config to existing folder
"log_folder": "C:\\Logs\\InfraTagging"
```

## Performance Tips

### 1. Use Proper Indexes

```sql
-- Speed up dependency queries
CREATE INDEX IDX_MAPPING_SOURCE 
ON INFRATAGGING_MAPPING(SOURCE_LAYERID, SOURCE_FEATUREID);

CREATE INDEX IDX_MAPPING_DEST
ON INFRATAGGING_MAPPING(DESTINATION_LAYERID, DESTINATION_FEATUREID);
```

### 2. Optimize SDE Connection

- Use direct connection (not through ArcGIS Server)
- Enable connection pooling if supported
- Use database views for complex queries

### 3. Batch Processing

The script already uses batching for INSERT operations (100 records per batch). Adjust if needed:

```python
batch_size = 100  # Change this value in save_to_cache_table()
```

### 4. Scheduled Execution

Run during off-peak hours:
- Night time (2:00 AM - 4:00 AM)
- Weekends
- Outside business hours

## Deployment to ArcGIS Server

### Step 1: Test Locally

```bash
python run_infratagging_job_sde.py --config config_sde.json
```

### Step 2: Prepare for Publishing

1. Ensure SDE connection file is accessible on ArcGIS Server
2. Common locations:
   ```
   C:\ProgramData\ESRI\connections\
   C:\ArcGIS\Connections\
   ```

3. Copy files to server:
   ```
   generate_infratagging_summary_sde.py
   InfraTaggingTools_SDE.pyt
   your_connection.sde
   ```

### Step 3: Publish from ArcGIS Pro

1. Run tool successfully in ArcGIS Pro
2. Share as Web Tool
3. Configure GP Service settings:
   - Execution Mode: **Asynchronous**
   - Max timeout: 3600 seconds
   - Result Map Server: Not required
   - Feature Access: Not required

4. Analyze and fix any issues
5. Publish to ArcGIS Server

### Step 4: Test GP Service

```python
import requests

url = "https://your-server/arcgis/rest/services/InfraTagging/GenerateInfrataggingSummary/GPServer/Generate%20Infratagging%20Summary%20Island%20Wide/submitJob"

params = {
    "sde_path": "C:\\ProgramData\\ESRI\\connections\\production.sde",
    "app_schema": "ONETOOLAPP.",
    "log_folder": "C:\\ArcGISServer\\logs\\infratagging",
    "f": "json"
}

response = requests.post(url, data=params)
print(response.json())
```

## Comparison: SDE vs pyodbc Version

### When to Use SDE Version

✅ **Use SDE Version when:**
- Running on ArcGIS Pro/Server
- Using enterprise geodatabase
- Want native ArcGIS integration
- Don't want to manage pyodbc installation
- Need versioned data support
- Prefer managed authentication (SDE connection)

### When to Use pyodbc Version

✅ **Use pyodbc Version when:**
- Running in non-ArcGIS Python environment
- Need direct SQL Server access
- Want more control over connections
- Running on systems without ArcGIS
- Need custom SQL Server features

### Feature Comparison

| Feature | SDE Version | pyodbc Version |
|---------|-------------|----------------|
| Requires ArcGIS | ✅ Yes | ❌ No |
| Additional packages | ❌ No | ✅ Yes (pyodbc) |
| Supports versioned data | ✅ Yes | ❌ No |
| Direct SQL access | ⚠️ Limited | ✅ Full |
| Connection management | 🔒 SDE file | 🔓 Connection string |
| Transaction support | ⚠️ Limited | ✅ Full |
| Enterprise geodatabase | ✅ Native | ⚠️ Via SQL |

## Monitoring

### Check Logs

```bash
# Windows
type C:\temp\GPLogs\20251123_InfraTaggingSummary.log

# Linux
cat /var/log/infratagging/20251123_InfraTaggingSummary.log
```

### Check Cache Table

```sql
-- See latest run
SELECT TOP 10 *
FROM ONETOOLAPP.INFRATAGGING_SUMMARY_CACHE
ORDER BY CREATED_DATE DESC;

-- Count records by type
SELECT 
    TYPE,
    CASE WHEN TYPE = 0 THEN 'Depending' ELSE 'Supporting' END AS TYPE_NAME,
    COUNT(*) AS RECORD_COUNT
FROM ONETOOLAPP.INFRATAGGING_SUMMARY_CACHE
GROUP BY TYPE;

-- Check for issues
SELECT 
    CATEGORY,
    CASE WHEN CATEGORY = 0 THEN 'No Issues' ELSE 'Has Issues' END AS STATUS,
    COUNT(*) AS COUNT
FROM ONETOOLAPP.INFRATAGGING_SUMMARY_CACHE
GROUP BY CATEGORY;
```

### Monitor GP Service

In ArcGIS Server Manager:
1. Navigate to **Logs**
2. Filter by service name
3. Check for errors or warnings
4. Review execution times

## Support

### Getting Help

1. **Check logs** first - they contain detailed error messages
2. **Test SDE connection** in ArcGIS Pro
3. **Verify database permissions**
4. **Run SQL queries manually** to isolate issues

### Common Log Messages

| Message | Meaning |
|---------|---------|
| "SDE connection initialized successfully" | ✅ Connection OK |
| "Retrieved N dependency links" | ✅ Query successful |
| "Successfully saved N records to cache" | ✅ Cache updated |
| "SQL execution failed" | ❌ SQL error |
| "Failed to connect to database" | ❌ Connection error |

## Summary

The **SDE Version** is ideal for ArcGIS-native deployments where:
- ✅ You're using ArcGIS Pro or ArcGIS Server
- ✅ You want enterprise geodatabase integration
- ✅ You prefer managed authentication via SDE connections
- ✅ You don't want to install additional Python packages

**Ready to get started?**
1. Create your SDE connection file in ArcGIS Pro
2. Copy `config_sde_example.json` to `config_sde.json`
3. Update configuration with your paths
4. Run: `python run_infratagging_job_sde.py --config config_sde.json`

---

**For detailed deployment instructions, see the original INFRATAGGING_DEPLOYMENT.md and adapt for SDE connections.**
