# Infrastructure Tagging Summary - Python GP Script

This document provides instructions for deploying the Infrastructure Tagging Summary generation tool as an ArcGIS Geoprocessing Service, replacing the .NET API endpoint.

## Overview

This Python geoprocessing script replicates the functionality of the .NET `GenerateInfrataggingSummaryIslandWide` API endpoint. It:

- Processes infrastructure tagging summaries for **Depending** and **Supporting** features
- Generates chart data for visualization
- Caches results in a SQL Server database
- Sends email notifications on completion
- Can be published as a GP service on ArcGIS Server

## Files Included

1. **generate_infratagging_summary.py** - Main Python script with processing logic
2. **InfraTaggingTools.pyt** - ArcGIS Python Toolbox for easy integration
3. **config_example.json** - Configuration file example
4. **INFRATAGGING_DEPLOYMENT.md** - This documentation file

## Prerequisites

### Software Requirements

- ArcGIS Pro 2.8+ or ArcGIS Server 10.8+
- Python 3.7+ (included with ArcGIS)
- SQL Server ODBC Driver 17 or later

### Python Dependencies

Install required Python packages:

```bash
# Open Python Command Prompt from ArcGIS Pro
conda activate arcgispro-py3

# Install required packages
pip install pyodbc
```

### Database Requirements

Ensure the following database objects exist:

- **Tables/Views:**
  - `INFRATAGGING_MAPPING` - Depending features mapping table
  - `INFRATAGGING_MAPPING_SUPP_VW` - Supporting features mapping view
  - `INFRATAGGING_LAYERS_VW` - Layer information view
  - `INFRA_CONS_STAGINGYR_VW` - Staging year information view
  - `INFRATAGGING_SUMMARY_CACHE` - Cache table for results

- **Cache Table Schema:**
```sql
CREATE TABLE INFRATAGGING_SUMMARY_CACHE (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    FEATUREID NVARCHAR(50),
    LAYER_ID INT,
    LAYER_NAME NVARCHAR(255),
    TYPE INT,  -- 0=Depending, 1=Supporting
    CATEGORY INT,  -- 0=No Issues, 1=Has Issues
    CHART_JSON NVARCHAR(MAX),
    CHART_HEIGHT INT,
    CREATED_DATE DATETIME
);
```

### Permissions

- SQL Server: Read access to source tables, Write access to cache table
- File System: Read/Write access to the script directory
- Network: SMTP access if email notifications are enabled

## Installation

### Step 1: Copy Files

1. Copy all files to a directory on your ArcGIS Server machine:
   ```
   C:\InfraTaggingGP\
   ├── generate_infratagging_summary.py
   ├── InfraTaggingTools.pyt
   └── config_example.json
   ```

### Step 2: Configure Database Connection

Edit the connection string in the toolbox parameters or create a configuration file:

```json
{
  "connection_string": "Driver={ODBC Driver 17 for SQL Server};Server=YOUR_SERVER;Database=YOUR_DATABASE;Trusted_Connection=yes;",
  "app_schema": "dbo"
}
```

For SQL Server Authentication:
```
Driver={ODBC Driver 17 for SQL Server};Server=YOUR_SERVER;Database=YOUR_DATABASE;UID=username;PWD=password;
```

### Step 3: Test Locally in ArcGIS Pro

1. Open ArcGIS Pro
2. Open the **Catalog Pane**
3. Navigate to **Toolboxes**
4. Right-click and select **Add Toolbox**
5. Browse to `InfraTaggingTools.pyt`
6. Expand the toolbox and double-click **Generate Infratagging Summary Island Wide**
7. Fill in parameters:
   - **Connection String**: Your SQL Server connection
   - **Schema Name**: Database schema (usually "dbo")
   - **Email Settings**: Optional email notification settings
8. Click **Run**

### Step 4: Publish as GP Service

#### Option A: Publish from ArcGIS Pro

1. Run the tool successfully in ArcGIS Pro (Step 3)
2. In the **Geoprocessing History**, right-click the completed tool run
3. Select **Share As** > **Web Tool**
4. Configure the GP Service:
   - **Name**: GenerateInfrataggingSummary
   - **Server**: Your ArcGIS Server connection
   - **Execution Mode**: Asynchronous (recommended for long-running process)
   - **Maximum number of records**: 5000
   - **Maximum timeout**: 3600 seconds (1 hour)
5. Click **Analyze** to check for issues
6. Click **Publish**

#### Option B: Publish via ArcGIS Server Manager

1. Package the toolbox and script:
   ```python
   import arcpy
   arcpy.PackageGPService(
       'C:\\InfraTaggingGP\\InfraTaggingTools.pyt\\GenerateInfrataggingSummary',
       'C:\\InfraTaggingGP\\InfraTaggingGP.gpk'
   )
   ```

2. Upload to ArcGIS Server:
   - Open ArcGIS Server Manager
   - Navigate to **Services** > **Publish Service**
   - Upload the .gpk file
   - Configure service properties

## Usage

### As a GP Service

Once published, call the GP service via REST API:

```python
import requests
import json

# GP Service URL
url = "https://your-server/arcgis/rest/services/InfraTagging/GenerateInfrataggingSummary/GPServer/Generate%20Infratagging%20Summary%20Island%20Wide/execute"

# Parameters
params = {
    "connection_string": "Driver={ODBC Driver 17 for SQL Server};Server=SERVER;Database=DB;Trusted_Connection=yes;",
    "app_schema": "dbo",
    "smtp_server": "smtp.company.com",
    "smtp_port": 587,
    "from_email": "noreply@company.com",
    "to_emails": "admin@company.com",
    "f": "json"
}

# Submit job
response = requests.post(url, data=params)
result = response.json()

print(f"Job ID: {result['jobId']}")
print(f"Status: {result['jobStatus']}")
```

### As a Scheduled Task

#### Windows Task Scheduler

Create a batch file (`run_infratagging.bat`):

```batch
@echo off
"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" ^
"C:\InfraTaggingGP\generate_infratagging_summary.py" ^
"Driver={ODBC Driver 17 for SQL Server};Server=SERVER;Database=DB;Trusted_Connection=yes;" ^
"dbo" ^
"smtp.company.com" ^
"587" ^
"noreply@company.com" ^
"admin@company.com"
```

Schedule in Task Scheduler:
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., Daily at 2:00 AM)
4. Action: Start a program
5. Program: `C:\InfraTaggingGP\run_infratagging.bat`

#### Linux Cron Job

```bash
# Edit crontab
crontab -e

# Add job to run daily at 2 AM
0 2 * * * /usr/bin/python3 /path/to/generate_infratagging_summary.py "connection_string" "schema"
```

## Configuration

### Email Notifications

Configure SMTP settings for email notifications:

```json
{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "from_email": "your-email@gmail.com",
  "to_emails": "recipient1@company.com,recipient2@company.com",
  "username": "your-email@gmail.com",
  "password": "your-app-password"
}
```

**For Gmail:**
- Use App Passwords (not regular password)
- Enable "Less secure app access" or use OAuth2

**For Office 365:**
```json
{
  "smtp_server": "smtp.office365.com",
  "smtp_port": 587,
  "use_tls": true
}
```

### Performance Tuning

For large datasets, adjust SQL Server settings:

```python
# In generate_infratagging_summary.py, modify SQL query:
stringBuilder.AppendLine("SET LOCK_TIMEOUT 30000;")  # Increase timeout
stringBuilder.AppendLine("SET QUERY_GOVERNOR_COST_LIMIT 0;")
stringBuilder.AppendLine("SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;")
```

### Logging

Logs are written to:
- **ArcGIS Pro**: Geoprocessing History
- **GP Service**: ArcGIS Server logs (`C:\arcgisserver\logs`)
- **Script Output**: Console/stdout

To enable file logging, modify the script:

```python
import logging

logging.basicConfig(
    filename='C:\\Logs\\infratagging.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

## Troubleshooting

### Common Issues

#### 1. "Module 'pyodbc' not found"

**Solution:**
```bash
# Activate ArcGIS Python environment
conda activate arcgispro-py3

# Install pyodbc
pip install pyodbc
```

#### 2. "Unable to connect to SQL Server"

**Checks:**
- Verify SQL Server is accessible from ArcGIS Server machine
- Test connection string using ODBC Data Sources
- Check firewall rules (port 1433)
- Verify SQL Server authentication mode

**Test Connection:**
```python
import pyodbc
conn = pyodbc.connect("YOUR_CONNECTION_STRING")
print("Connection successful!")
```

#### 3. "Table does not exist"

**Solution:**
- Verify schema name is correct
- Check user has permissions to access tables
- Confirm table names match exactly (case-sensitive in some SQL Server configurations)

#### 4. GP Service times out

**Solution:**
- Increase service timeout in ArcGIS Server Manager
- Set execution mode to **Asynchronous**
- Optimize SQL queries with indexes
- Consider batching large datasets

### Debug Mode

Enable detailed logging:

```python
# Add to top of generate_infratagging_summary.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Migrating from .NET API

### API Endpoint Replacement

Replace .NET endpoint calls:

**Old (.NET API):**
```csharp
// HTTP GET
var response = await httpClient.GetAsync(
    "https://api.company.com/api/infratagging/GenerateInfrataggingSummaryIslandWide"
);
```

**New (GP Service):**
```python
import requests

response = requests.post(
    "https://gis.company.com/arcgis/rest/services/InfraTagging/GenerateInfrataggingSummary/GPServer/Generate%20Infratagging%20Summary%20Island%20Wide/submitJob",
    data={
        "connection_string": "...",
        "app_schema": "dbo",
        "f": "json"
    }
)
```

### Scheduled Jobs

Replace .NET scheduled tasks with:
1. Windows Task Scheduler (Windows Server)
2. Cron jobs (Linux)
3. ArcGIS Server scheduled jobs

### Monitoring

Instead of .NET application logs, monitor via:
- ArcGIS Server Manager > Logs
- Database query: `SELECT * FROM INFRATAGGING_SUMMARY_CACHE ORDER BY CREATED_DATE DESC`
- Email notifications

## Performance Optimization

### Database Indexing

Create indexes on frequently queried columns:

```sql
-- Index on mapping tables
CREATE INDEX IDX_INFRATAGGING_MAPPING_SOURCE 
ON INFRATAGGING_MAPPING(SOURCE_LAYERID, SOURCE_FEATUREID);

CREATE INDEX IDX_INFRATAGGING_MAPPING_DEST
ON INFRATAGGING_MAPPING(DESTINATION_LAYERID, DESTINATION_FEATUREID);

-- Index on layers view
CREATE INDEX IDX_INFRATAGGING_LAYERS_NAME
ON INFRATAGGING_LAYERS_VW(LAYER_NAME);
```

### Batch Processing

For very large datasets, process in batches:

```python
# Modify process_infratagging_summary to process in chunks
BATCH_SIZE = 1000
for i in range(0, len(self.dependency_all), BATCH_SIZE):
    batch = self.dependency_all[i:i+BATCH_SIZE]
    # Process batch...
```

### Caching

Implement caching for layer information:

```python
# Cache layer info to avoid repeated queries
self._layer_cache = {}

def get_infra_layers(self):
    if not self._layer_cache:
        self._layer_cache = self._fetch_layers_from_db()
    return self._layer_cache
```

## Security Considerations

### Connection String Security

**Don't hardcode credentials!** Use:

1. **Windows Authentication** (recommended):
   ```
   Trusted_Connection=yes;
   ```

2. **Environment Variables**:
   ```python
   import os
   password = os.environ.get('SQL_PASSWORD')
   ```

3. **Encrypted Configuration**:
   ```python
   from cryptography.fernet import Fernet
   # Decrypt connection string at runtime
   ```

### Service Security

Configure GP Service security in ArcGIS Server Manager:
- Enable HTTPS
- Restrict access to specific users/groups
- Use token-based authentication
- Set appropriate CORS policies

## Support and Maintenance

### Version History

- **v1.0** (2025-11-23): Initial conversion from .NET API

### Known Limitations

1. Large datasets (>100,000 records) may require extended timeout
2. Email notifications require SMTP access from server
3. Chart generation assumes specific date formats

### Future Enhancements

- [ ] Add support for incremental updates (only process changed features)
- [ ] Implement parallel processing for better performance
- [ ] Add REST API wrapper for easier integration
- [ ] Create web interface for monitoring and management

## Contact

For issues or questions:
- Check ArcGIS Server logs
- Review database connection settings
- Contact GIS administrator

---

## Quick Start Checklist

- [ ] Install pyodbc package
- [ ] Configure SQL Server connection string
- [ ] Test script locally in ArcGIS Pro
- [ ] Verify database tables exist and are accessible
- [ ] Publish as GP service to ArcGIS Server
- [ ] Test GP service via REST API
- [ ] Configure scheduled execution (if needed)
- [ ] Set up email notifications
- [ ] Monitor initial runs and verify cache table updates

---

**Last Updated:** 2025-11-23
