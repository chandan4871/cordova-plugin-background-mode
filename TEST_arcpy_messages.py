"""
Simple test script to verify arcpy.AddMessage works
Matches the pattern from your working OnetoolEpacsMatrixSync.py script
"""

import arcpy
import logging
import os
import time

# Configuration
LogFolder = r"C:\temp\GPLogs"  # Update if needed
LogFile = time.strftime("%Y%m%d_%H%M") + '_TEST_Messages.log'

def prepareLogFile():
    """Prepare the log file"""
    if not os.path.exists(LogFolder):
        os.makedirs(LogFolder)
    logging.basicConfig(
        filename=os.path.join(LogFolder, LogFile),
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

def main():
    prepareLogFile()
    
    try:
        # Test 1: Simple message
        arcpy.AddMessage("="*80)
        arcpy.AddMessage("TEST SCRIPT - Verifying arcpy.AddMessage")
        arcpy.AddMessage("="*80)
        logging.info("Test script started")
        
        # Test 2: Multiple messages
        arcpy.AddMessage("Test Message 1: This is a simple test")
        logging.info("Test Message 1: This is a simple test")
        
        arcpy.AddMessage("Test Message 2: Counting to 5...")
        for i in range(1, 6):
            arcpy.AddMessage(f"  Count: {i}")
            logging.info(f"  Count: {i}")
        
        # Test 3: Success message
        arcpy.AddMessage("="*80)
        arcpy.AddMessage("✓ TEST COMPLETED SUCCESSFULLY")
        arcpy.AddMessage("="*80)
        arcpy.AddMessage(f"Log file created: {os.path.join(LogFolder, LogFile)}")
        logging.info("Test completed successfully")
        
        # Test 4: Warning
        arcpy.AddWarning("This is a test warning message")
        logging.warning("This is a test warning message")
        
        # Test 5: Summary
        arcpy.AddMessage("="*80)
        arcpy.AddMessage("SUMMARY:")
        arcpy.AddMessage("  - Test Messages: 5")
        arcpy.AddMessage("  - Test Warnings: 1")
        arcpy.AddMessage("  - Test Errors: 0")
        arcpy.AddMessage("="*80)
        
    except Exception as ex:
        arcpy.AddError(f"Error in test script: {ex}")
        logging.error(f"Error in test script: {ex}")

if __name__ == '__main__':
    main()
    arcpy.AddMessage("Script execution completed")
