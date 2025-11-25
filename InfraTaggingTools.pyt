"""
ArcGIS Python Toolbox for Infrastructure Tagging Summary Generation

This toolbox contains tools for processing infrastructure tagging data
and generating summary reports that can be published as GP services.
"""

import arcpy
import os


class Toolbox(object):
    def __init__(self):
        """Define the toolbox properties"""
        self.label = "Infrastructure Tagging Tools"
        self.alias = "InfraTagging"
        
        # List of tool classes associated with this toolbox
        self.tools = [GenerateInfrataggingSummary]


class GenerateInfrataggingSummary(object):
    def __init__(self):
        """Define the tool properties"""
        self.label = "Generate Infratagging Summary Island Wide"
        self.description = """
        Processes infrastructure tagging summaries for Depending and Supporting features
        and caches the results with chart data. This tool replicates the .NET API 
        endpoint functionality for ArcGIS Server deployment.
        """
        self.canRunInBackground = True
        
    def getParameterInfo(self):
        """Define parameter definitions"""
        
        # Parameter 0: Connection String
        param0 = arcpy.Parameter(
            displayName="SQL Server Connection String",
            name="connection_string",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param0.value = "Driver={ODBC Driver 17 for SQL Server};Server=YOUR_SERVER;Database=YOUR_DATABASE;Trusted_Connection=yes;"
        
        # Parameter 1: Database Schema
        param1 = arcpy.Parameter(
            displayName="Database Schema Name",
            name="app_schema",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param1.value = "dbo"
        
        # Parameter 2: SMTP Server
        param2 = arcpy.Parameter(
            displayName="SMTP Server (Optional)",
            name="smtp_server",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        param2.category = "Email Configuration"
        
        # Parameter 3: SMTP Port
        param3 = arcpy.Parameter(
            displayName="SMTP Port",
            name="smtp_port",
            datatype="GPLong",
            parameterType="Optional",
            direction="Input")
        param3.value = 587
        param3.category = "Email Configuration"
        
        # Parameter 4: From Email
        param4 = arcpy.Parameter(
            displayName="From Email Address",
            name="from_email",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        param4.category = "Email Configuration"
        
        # Parameter 5: To Emails
        param5 = arcpy.Parameter(
            displayName="To Email Addresses (comma-separated)",
            name="to_emails",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        param5.category = "Email Configuration"
        
        # Parameter 6: Email Username
        param6 = arcpy.Parameter(
            displayName="Email Username (Optional)",
            name="email_username",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        param6.category = "Email Configuration"
        
        # Parameter 7: Email Password
        param7 = arcpy.Parameter(
            displayName="Email Password (Optional)",
            name="email_password",
            datatype="GPStringHidden",
            parameterType="Optional",
            direction="Input")
        param7.category = "Email Configuration"
        
        # Parameter 8: Output Status
        param8 = arcpy.Parameter(
            displayName="Execution Status",
            name="status",
            datatype="GPString",
            parameterType="Derived",
            direction="Output")
        
        params = [param0, param1, param2, param3, param4, param5, param6, param7, param8]
        return params
        
    def isLicensed(self):
        """Set whether tool is licensed to execute"""
        return True
        
    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed. This method is called whenever a parameter
        has been changed."""
        return
        
    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        
        # Validate connection string
        if parameters[0].altered:
            conn_str = parameters[0].valueAsText
            if "Server=" not in conn_str or "Database=" not in conn_str:
                parameters[0].setErrorMessage("Invalid connection string format")
                
        # Validate email configuration
        email_params = [parameters[2], parameters[4], parameters[5]]  # SMTP, From, To
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
            connection_string = parameters[0].valueAsText
            app_schema = parameters[1].valueAsText
            smtp_server = parameters[2].valueAsText
            smtp_port = parameters[3].value if parameters[3].value else 587
            from_email = parameters[4].valueAsText
            to_emails = parameters[5].valueAsText
            email_username = parameters[6].valueAsText
            email_password = parameters[7].valueAsText
            
            # Import the processor module
            import sys
            script_dir = os.path.dirname(os.path.abspath(__file__))
            if script_dir not in sys.path:
                sys.path.insert(0, script_dir)
                
            from generate_infratagging_summary import InfraTaggingProcessor
            
            # Build email configuration
            email_config = None
            if smtp_server and from_email and to_emails:
                email_config = {
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
            processor = InfraTaggingProcessor(connection_string, app_schema, email_config)
            
            # Execute processing
            status = processor.execute()
            
            # Set output parameter
            arcpy.SetParameterAsText(8, status)
            
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
            arcpy.SetParameterAsText(8, "Failed")
            
        return
