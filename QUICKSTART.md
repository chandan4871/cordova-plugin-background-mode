# Quick Start Guide - Infrastructure Tagging GP Tool

Get up and running in 5 minutes!

## Step 1: Install Dependencies (2 minutes)

Open Python Command Prompt from ArcGIS Pro:

```bash
# Activate ArcGIS Python environment
conda activate arcgispro-py3

# Install required package
pip install pyodbc
```

## Step 2: Configure Database Connection (1 minute)

Create a file named `config.json` (copy from `config_production.json`):

```json
{
  "database": {
    "connection_string": "Driver={ODBC Driver 17 for SQL Server};Server=YOUR_SERVER;Database=YOUR_DB;Trusted_Connection=yes;",
    "app_schema": "dbo"
  },
  "email": {
    "enabled": false
  }
}
```

**Replace:**
- `YOUR_SERVER` with your SQL Server name
- `YOUR_DB` with your database name

## Step 3: Validate Setup (1 minute)

```bash
python test_setup.py --connection "YOUR_CONNECTION_STRING" --schema "dbo"
```

If all tests pass, you're ready!

## Step 4: Test Run (1 minute)

```bash
python run_infratagging_job.py --config config.json
```

## Step 5: Publish to ArcGIS Server (Optional)

1. Open ArcGIS Pro
2. Add Toolbox: `InfraTaggingTools.pyt`
3. Run the tool successfully once
4. Right-click the tool run in Geoprocessing History
5. Select **Share As** > **Web Tool**
6. Configure and **Publish**

---

## Common Connection Strings

### Windows Authentication (Recommended)
```
Driver={ODBC Driver 17 for SQL Server};Server=MYSERVER;Database=MYDB;Trusted_Connection=yes;
```

### SQL Server Authentication
```
Driver={ODBC Driver 17 for SQL Server};Server=MYSERVER;Database=MYDB;UID=username;PWD=password;
```

### Named Instance
```
Driver={ODBC Driver 17 for SQL Server};Server=MYSERVER\\INSTANCE;Database=MYDB;Trusted_Connection=yes;
```

### With Port Number
```
Driver={ODBC Driver 17 for SQL Server};Server=MYSERVER,1433;Database=MYDB;Trusted_Connection=yes;
```

---

## Troubleshooting

### "Module 'pyodbc' not found"
```bash
pip install pyodbc
```

### "Cannot connect to SQL Server"
- Verify server name and database name
- Check firewall allows port 1433
- Test with SQL Server Management Studio first

### "Table does not exist"
- Verify schema name (usually "dbo")
- Check you have read permissions
- Run: `SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME LIKE 'INFRA%'`

---

## Next Steps

✓ See **INFRATAGGING_DEPLOYMENT.md** for detailed documentation

✓ Configure email notifications in `config.json`

✓ Set up scheduled execution (Task Scheduler / Cron)

✓ Publish as GP service for web access

---

## Need Help?

1. Run validation: `python test_setup.py --connection "..." --schema "dbo"`
2. Check ArcGIS Server logs
3. Review database permissions
4. Verify table names and schema

---

**You're all set!** 🚀
