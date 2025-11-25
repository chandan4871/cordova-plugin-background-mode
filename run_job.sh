#!/bin/bash
################################################################################
# Infrastructure Tagging Summary Generation - Linux/Unix Shell Script
################################################################################
#
# This shell script runs the infrastructure tagging summary generation
# using the Python script. Edit the variables below to match your setup.
#
# Usage: ./run_job.sh
#
# To schedule with cron:
#   crontab -e
#   Add: 0 2 * * * /path/to/run_job.sh >> /var/log/infratagging.log 2>&1
#
################################################################################

echo "========================================================================"
echo "Infrastructure Tagging Summary Generation"
echo "========================================================================"
echo ""

################################################################################
# CONFIGURATION - Edit these variables
################################################################################

# Path to Python executable
PYTHON_EXE="/usr/bin/python3"

# Path to the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Configuration file path
CONFIG_FILE="${SCRIPT_DIR}/config.json"

# Alternatively, you can specify connection details directly:
# CONNECTION_STRING="Driver={ODBC Driver 17 for SQL Server};Server=YOUR_SERVER;Database=YOUR_DB;Trusted_Connection=yes;"
# SCHEMA_NAME="dbo"

################################################################################
# END CONFIGURATION
################################################################################

# Change to script directory
cd "$SCRIPT_DIR"

# Check if Python exists
if [ ! -f "$PYTHON_EXE" ]; then
    echo "ERROR: Python executable not found at: $PYTHON_EXE"
    echo "Please update PYTHON_EXE variable in this script."
    echo ""
    exit 1
fi

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: Configuration file not found at: $CONFIG_FILE"
    echo "Please create config.json or update CONFIG_FILE variable."
    echo ""
    exit 1
fi

# Check if script file exists
if [ ! -f "${SCRIPT_DIR}/run_infratagging_job.py" ]; then
    echo "ERROR: Python script not found at: ${SCRIPT_DIR}/run_infratagging_job.py"
    echo ""
    exit 1
fi

# Run the script
echo "Starting job..."
echo ""

"$PYTHON_EXE" "${SCRIPT_DIR}/run_infratagging_job.py" --config "$CONFIG_FILE"

# Capture exit code
EXIT_CODE=$?

echo ""
echo "========================================================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "Job completed successfully!"
else
    echo "Job failed with exit code: $EXIT_CODE"
fi
echo "========================================================================"
echo ""

exit $EXIT_CODE
