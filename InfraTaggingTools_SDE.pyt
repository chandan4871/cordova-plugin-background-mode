"""
ArcGIS Python Toolbox for Infrastructure Tagging Summary Generation (SDE Version)

This toolbox contains tools for processing infrastructure tagging data
using SDE connections and generating summary reports that can be published as GP services.
"""

import arcpy
import os


class Toolbox(object):
    def __init__(self):
        """Define the toolbox properties"""
        self.label = "Infrastructure Tagging Tools (SDE)"
        self.alias = "InfraTaggingSDE"
        
        # List of tool classes associated with this toolbox
        self.tools = [GenerateInfrataggingSummary]


class GenerateInfrataggingSummary(object):
    def __init__(self):
        """Define the tool properties"""
        self.label = "Generate Infratagging Summary Island Wide"
        self.description = """
        Processes infrastructure tagging summaries for Depending and Supporting features
        and caches the results with chart data. This tool uses SDE connections for
        database access and can be published as a GP service on ArcGIS Server.
        """
        self.canRunInBackground = True
        
    def getParameterInfo(self):
        """Define parameter definitions"""
        
        # Parameter 0: SDE Connection File
        param0 = arcpy.Parameter(
            displayName="SDE Connection File",
            name="sde_path",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")
        param0.filter.list = ["Remote Database"]
        
        # Parameter 1: Database Schema
        param1 = arcpy.Parameter(
            displayName="Database Schema Name (with trailing dot)",
            name="app_schema",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param1.value = "ONETOOLAPP."
        
        # Parameter 2: Log Folder
        param2 = arcpy.Parameter(
            displayName="Log Folder Path",
            name="log_folder",
            datatype="DEFolder",
            parameterType="Optional",
            direction="Input")
        param2.value = r"C:\temp\GPLogs"
        
        # Parameter 3: SMTP Server
        param3 = arcpy.Parameter(
            displayName="SMTP Server (Optional)",
            name="smtp_server",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        param3.category = "Email Configuration"
        
        # Parameter 4: SMTP Port
        param4 = arcpy.Parameter(
            displayName="SMTP Port",
            name="smtp_port",
            datatype="GPLong",
            parameterType="Optional",
            direction="Input")
        param4.value = 587
        param4.category = "Email Configuration"
        
        # Parameter 5: From Email
        param5 = arcpy.Parameter(
            displayName="From Email Address",
            name="from_email",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        param5.category = "Email Configuration"
        
        # Parameter 6: To Emails
        param6 = arcpy.Parameter(
            displayName="To Email Addresses (comma-separated)",
            name="to_emails",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        param6.category = "Email Configuration"
        
        # Parameter 7: Email Username
        param7 = arcpy.Parameter(
            displayName="Email Username (Optional)",
            name="email_username",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        param7.category = "Email Configuration"
        
        # Parameter 8: Email Password
        param8 = arcpy.Parameter(
            displayName="Email Password (Optional)",
            name="email_password",
            datatype="GPStringHidden",
            parameterType="Optional",
            direction="Input")
        param8.category = "Email Configuration"
        
        # Parameter 9: Output Status
        param9 = arcpy.Parameter(
            displayName="Execution Status",
            name="status",
            datatype="GPString",
            parameterType="Derived",
            direction="Output")
        
        params = [param0, param1, param2, param3, param4, param5, param6, param7, param8, param9]
        return params
        
    def isLicensed(self):
        """Set whether tool is licensed to execute"""
        return True
        
    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed. This method is called whenever a parameter
        has been changed."""
        
        # Ensure schema has trailing dot
        if parameters[1].altered and parameters[1].valueAsText:
            schema = parameters[1].valueAsText
            if not schema.endswith('.'):
                parameters[1].value = schema + '.'
                
        return
        
    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        
        # Validate SDE connection file
        if parameters[0].altered and parameters[0].valueAsText:
            sde_path = parameters[0].valueAsText
            if not sde_path.lower().endswith('.sde'):
                parameters[0].setErrorMessage("Please select a valid SDE connection file (.sde)")
                
        # Validate schema name
        if parameters[1].altered and parameters[1].valueAsText:
            schema = parameters[1].valueAsText
            if not schema.endswith('.'):
                parameters[1].setWarningMessage("Schema name should end with a dot (e.g., 'ONETOOLAPP.')")
                
        # Validate email configuration
        email_params = [parameters[3], parameters[5], parameters[6]]  # SMTP, From, To
        filled_params = [p for p in email_params if p.valueAsText]
        
        if filled_params and len(filled_params) < 3:
            for param in email_params:
                if not param.valueAsText:
                    param.setWarningMessage("All email configuration fields should be provided for email notifications")
        
        return
        
    def execute(self, parameters, messages):
        """The source code of the tool"""
        
        try:
            # Get parameter values
            sde_path = parameters[0].valueAsText
            app_schema = parameters[1].valueAsText
            log_folder = parameters[2].valueAsText
            smtp_server = parameters[3].valueAsText
            smtp_port = parameters[4].value if parameters[4].value else 587
            from_email = parameters[5].valueAsText
            to_emails = parameters[6].valueAsText
            email_username = parameters[7].valueAsText
            email_password = parameters[8].valueAsText
            
            # Ensure schema has trailing dot
            if app_schema and not app_schema.endswith('.'):
                app_schema = app_schema + '.'
            
            # Import the processor module
            import sys
            script_dir = os.path.dirname(os.path.abspath(__file__))
            if script_dir not in sys.path:
                sys.path.insert(0, script_dir)
                
            from generate_infratagging_summary_sde import InfraTaggingProcessor
            
            # Build email configuration
            email_config = None
            if smtp_server and from_email and to_emails:
                email_config = {
                    'enabled': True,
                    'smtp_server': smtp_server,
                    'smtp_port': smtp_port,
                    'from_email': from_email,
                    'to_emails': [e.strip() for e in to_emails.split(',')],
                    'username': email_username,
                    'password': email_password
                }
                arcpy.AddMessage("Email notifications enabled")
            else:
                arcpy.AddMessage("Email notifications disabled")
            
            # Create processor instance
            processor = InfraTaggingProcessor(sde_path, app_schema, log_folder, email_config)
            
            # Execute processing
            status = processor.execute()
            
            # Set output parameter
            arcpy.SetParameterAsText(9, status)
            
            if status == "Success":
                arcpy.AddMessage("="*80)
                arcpy.AddMessage("Job completed successfully!")
                arcpy.AddMessage("="*80)
            else:
                arcpy.AddError("="*80)
                arcpy.AddError("Job failed. Check logs for details.")
                arcpy.AddError("="*80)
                
        except Exception as e:
            arcpy.AddError(f"Fatal error: {str(e)}")
            import traceback
            arcpy.AddError(traceback.format_exc())
            arcpy.SetParameterAsText(9, "Failed")
            
        return
