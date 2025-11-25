# Infrastructure Tagging Summary - Python GP Tool

## Overview

This package contains a Python geoprocessing tool that replaces the .NET API endpoint `GenerateInfrataggingSummaryIslandWide`. It processes infrastructure tagging data for depending and supporting features, generates chart visualizations, and caches results in a SQL Server database.

## What This Does

The tool performs the following operations:

1. **Processes Depending Features**: Analyzes infrastructure dependencies where features depend on other infrastructure
2. **Processes Supporting Features**: Analyzes infrastructure that supports other features
3. **Generates Chart Data**: Creates JSON chart data for Gantt-style schedule visualization
4. **Caches Results**: Stores processed data in `INFRATAGGING_SUMMARY_CACHE` table
5. **Sends Notifications**: Optional email notifications on job completion
6. **Logs Progress**: Comprehensive logging throughout execution

## Package Contents

### Core Scripts

| File | Purpose |
|------|---------|
| **generate_infratagging_summary.py** | Main Python module with all processing logic |
| **InfraTaggingTools.pyt** | ArcGIS Python Toolbox for GP tool integration |
| **run_infratagging_job.py** | Standalone runner (can run without ArcGIS) |
| **test_setup.py** | Setup validation and testing script |

### Configuration Files

| File | Purpose |
|------|---------|
| **config_example.json** | Basic configuration example |
| **config_production.json** | Comprehensive production configuration template |
| **requirements.txt** | Python package dependencies |

### Execution Scripts

| File | Purpose |
|------|---------|
| **run_job.bat** | Windows batch file for easy execution |
| **run_job.sh** | Linux/Unix shell script for easy execution |

### Documentation

| File | Purpose |
|------|---------|
| **QUICKSTART.md** | 5-minute quick start guide |
| **INFRATAGGING_DEPLOYMENT.md** | Comprehensive deployment documentation |
| **README_INFRATAGGING.md** | This file - package overview |

## Quick Start (5 Minutes)

### 1. Install Dependencies
```bash
pip install pyodbc
```

### 2. Configure Database
Create `config.json`:
```json
{
  "database": {
    "connection_string": "Driver={ODBC Driver 17 for SQL Server};Server=YOUR_SERVER;Database=YOUR_DB;Trusted_Connection=yes;",
    "app_schema": "dbo"
  }
}
```

### 3. Test Setup
```bash
python test_setup.py --connection "YOUR_CONNECTION_STRING" --schema "dbo"
```

### 4. Run Job
```bash
# Using config file
python run_infratagging_job.py --config config.json

# OR using Windows batch file
run_job.bat

# OR using Linux shell script
./run_job.sh
```

## Deployment Options

### Option 1: ArcGIS Geoprocessing Service (Recommended)

Publish as a GP service on ArcGIS Server for web-based access.

**Pros:**
- Web-accessible via REST API
- Integrated with ArcGIS ecosystem
- Supports asynchronous execution
- Built-in monitoring and logging

**How to Deploy:**
1. Open ArcGIS Pro
2. Add toolbox: `InfraTaggingTools.pyt`
3. Run tool successfully once
4. Share as Web Tool to ArcGIS Server

**Access via REST:**
```
https://your-server/arcgis/rest/services/InfraTagging/GenerateInfrataggingSummary/GPServer
```

See: **INFRATAGGING_DEPLOYMENT.md** for detailed steps

### Option 2: Scheduled Task (Windows Task Scheduler)

Run on a schedule without ArcGIS Server.

**Pros:**
- Simple setup
- No ArcGIS Server license required
- Direct execution on database server
- Good for nightly batch jobs

**How to Deploy:**
1. Edit `run_job.bat` with your settings
2. Open Windows Task Scheduler
3. Create new task
4. Set schedule (e.g., daily at 2 AM)
5. Action: Run `run_job.bat`

### Option 3: Linux Cron Job

Run on Linux servers via cron.

**Pros:**
- Native Linux scheduling
- Simple and reliable
- Low resource usage
- Easy to monitor via logs

**How to Deploy:**
```bash
# Edit crontab
crontab -e

# Add job (runs daily at 2 AM)
0 2 * * * /path/to/run_job.sh >> /var/log/infratagging.log 2>&1
```

### Option 4: Standalone Python Script

Run manually or via custom integration.

**Pros:**
- Maximum flexibility
- Easy to integrate with other systems
- Can be called from other applications
- Good for testing and debugging

**How to Run:**
```bash
python run_infratagging_job.py --config config.json
```

## Architecture

### Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    SQL Server Database                       │
├─────────────────────────────────────────────────────────────┤
│  • INFRATAGGING_MAPPING (Depending features)                │
│  • INFRATAGGING_MAPPING_SUPP_VW (Supporting features)       │
│  • INFRATAGGING_LAYERS_VW (Layer metadata)                  │
│  • INFRA_CONS_STAGINGYR_VW (Schedule data)                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Python Processing Engine                        │
├─────────────────────────────────────────────────────────────┤
│  1. Fetch dependency links (Depending & Supporting)         │
│  2. Process each feature                                    │
│  3. Filter schedule links                                   │
│  4. Check for conflicts/issues                              │
│  5. Generate chart JSON data                                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 Cache & Notify                              │
├─────────────────────────────────────────────────────────────┤
│  • Save to INFRATAGGING_SUMMARY_CACHE                       │
│  • Send email notification                                  │
│  • Log results                                              │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

#### InfraTaggingProcessor Class
- Main processing engine
- Handles database connections
- Coordinates all operations
- Manages logging and error handling

#### Processing Methods
- `get_dependency_links_all()` - Fetch dependency data
- `process_infratagging_summary()` - Process by type
- `filter_schedule_links()` - Filter and analyze schedules
- `get_schedule_data_island_wide()` - Generate island-wide view
- `prepare_chart_json_data()` - Create chart visualizations
- `add_to_summary_cache_results()` - Cache results

## Database Requirements

### Required Tables/Views

```sql
-- Mapping tables
INFRATAGGING_MAPPING
INFRATAGGING_MAPPING_SUPP_VW

-- Metadata views
INFRATAGGING_LAYERS_VW
INFRA_CONS_STAGINGYR_VW

-- Cache table (must have write access)
INFRATAGGING_SUMMARY_CACHE
```

### Cache Table Schema

```sql
CREATE TABLE INFRATAGGING_SUMMARY_CACHE (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    FEATUREID NVARCHAR(50) NOT NULL,
    LAYER_ID INT NOT NULL,
    LAYER_NAME NVARCHAR(255) NOT NULL,
    TYPE INT NOT NULL,  -- 0=Depending, 1=Supporting
    CATEGORY INT NOT NULL,  -- 0=No Issues, 1=Has Issues
    CHART_JSON NVARCHAR(MAX),
    CHART_HEIGHT INT,
    CREATED_DATE DATETIME DEFAULT GETDATE()
);

-- Recommended indexes
CREATE INDEX IDX_CACHE_FEATURE ON INFRATAGGING_SUMMARY_CACHE(FEATUREID, LAYER_ID);
CREATE INDEX IDX_CACHE_TYPE ON INFRATAGGING_SUMMARY_CACHE(TYPE);
CREATE INDEX IDX_CACHE_CREATED ON INFRATAGGING_SUMMARY_CACHE(CREATED_DATE);
```

## Configuration

### Basic Configuration

Minimum required configuration:

```json
{
  "database": {
    "connection_string": "Driver={ODBC Driver 17 for SQL Server};Server=SERVER;Database=DB;Trusted_Connection=yes;",
    "app_schema": "dbo"
  }
}
```

### Full Configuration

See `config_production.json` for all available options including:
- Email notifications
- Performance tuning
- Logging settings
- Processing options
- Monitoring configuration

## Email Notifications

Enable email notifications to get job status updates:

```json
{
  "email": {
    "enabled": true,
    "smtp_server": "smtp.office365.com",
    "smtp_port": 587,
    "from_email": "noreply@company.com",
    "to_emails": ["admin@company.com", "team@company.com"],
    "username": "noreply@company.com",
    "password": "your_password"
  }
}
```

Emails are sent on:
- ✅ Successful completion
- ❌ Errors or failures
- 📊 Include processing statistics

## Monitoring and Logging

### Log Locations

- **ArcGIS Pro**: Geoprocessing History pane
- **GP Service**: `C:\arcgisserver\logs\`
- **Standalone**: Console output or specified log file

### Log Contents

Logs include:
- Execution timestamps
- Record counts processed
- Errors and warnings
- Database operations
- Email status

### Monitoring Best Practices

1. **Check logs regularly** for errors
2. **Monitor execution time** - alert if exceeds threshold
3. **Verify cache updates** - check `CREATED_DATE` in cache table
4. **Track record counts** - ensure consistent processing
5. **Test email notifications** periodically

## Performance Considerations

### For Large Datasets (>10,000 records)

1. **Increase timeout settings**
   ```json
   "performance": {
     "sql_timeout_seconds": 600
   }
   ```

2. **Add database indexes**
   ```sql
   CREATE INDEX IDX_MAPPING_SOURCE ON INFRATAGGING_MAPPING(SOURCE_LAYERID, SOURCE_FEATUREID);
   ```

3. **Use asynchronous GP service** (not synchronous)

4. **Schedule during off-peak hours** (e.g., 2 AM)

### Expected Performance

| Records | Execution Time |
|---------|---------------|
| 1,000 | 30 seconds |
| 10,000 | 5 minutes |
| 50,000 | 20-30 minutes |
| 100,000+ | 45-60 minutes |

*Times vary based on database server performance and network*

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "pyodbc not found" | `pip install pyodbc` |
| "Cannot connect to database" | Check connection string and firewall |
| "Table does not exist" | Verify schema name and permissions |
| "GP service timeout" | Increase timeout, use asynchronous mode |
| "Email failed to send" | Check SMTP settings and credentials |

### Validation

Run the validation script to diagnose issues:

```bash
python test_setup.py --connection "YOUR_CONNECTION_STRING" --schema "dbo"
```

This checks:
- ✓ Python version
- ✓ Required packages
- ✓ Database connectivity
- ✓ Table existence
- ✓ Permissions
- ✓ Sample data

## Comparison: .NET vs Python

| Aspect | .NET API | Python GP Tool |
|--------|----------|----------------|
| **Deployment** | IIS / Web Server | ArcGIS Server |
| **Access** | HTTP REST API | GP Service REST API |
| **Scheduling** | Windows Service | Task Scheduler / Cron |
| **Dependencies** | .NET Framework | Python + pyodbc |
| **Integration** | Web applications | ArcGIS ecosystem |
| **Maintenance** | C# code | Python scripts |
| **Logging** | Application logs | ArcGIS logs |
| **Monitoring** | Custom dashboard | ArcGIS Server Manager |

## Migration from .NET API

### API Endpoint Mapping

| .NET Endpoint | Python GP Service |
|---------------|-------------------|
| `GET /api/infratagging/GenerateInfrataggingSummaryIslandWide` | `POST /arcgis/rest/.../GPServer/.../execute` |

### Response Format

Both return status: "Success" or "Failed"

**Python GP Service Response:**
```json
{
  "jobId": "j123...",
  "jobStatus": "esriJobSucceeded",
  "results": {
    "status": "Success"
  }
}
```

## Support

### Getting Help

1. **Read documentation**: Start with QUICKSTART.md
2. **Run validation**: `python test_setup.py`
3. **Check logs**: Review execution logs for errors
4. **Test database**: Verify connectivity and permissions

### Best Practices

✅ **DO:**
- Use Windows Authentication when possible
- Schedule during off-peak hours
- Enable email notifications
- Monitor logs regularly
- Keep backups of configuration files

❌ **DON'T:**
- Hardcode passwords in scripts
- Run during peak business hours
- Ignore validation errors
- Skip testing before production deployment

## Updates and Maintenance

### Version History

- **v1.0** (2025-11-23): Initial release
  - Converted from .NET API
  - Full feature parity
  - ArcGIS GP tool integration

### Maintenance Tasks

- **Weekly**: Check logs for errors
- **Monthly**: Verify cache table size
- **Quarterly**: Review and optimize performance
- **Annually**: Update dependencies and test

## License

This tool is provided as-is for use within your organization.

## Credits

Converted from .NET API endpoint `GenerateInfrataggingSummaryIslandWide` to Python geoprocessing tool compatible with ArcGIS Server.

---

**Ready to deploy?** Start with **QUICKSTART.md** for a 5-minute setup guide!

**Need details?** See **INFRATAGGING_DEPLOYMENT.md** for comprehensive documentation!
