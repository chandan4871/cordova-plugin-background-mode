"""
ArcGIS Geoprocessing Script: Generate Infratagging Summary Island Wide
This script processes infrastructure tagging summaries for Depending and Supporting features
and caches the results with chart data.

Author: Converted from .NET API
Date: 2025-11-23
"""

import arcpy
import pyodbc
import json
import datetime
import traceback
from typing import List, Dict, Tuple, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class InfraTaggingProcessor:
    """Main processor class for infrastructure tagging summary generation"""
    
    def __init__(self, connection_string: str, app_schema: str, email_config: Dict = None):
        """
        Initialize the processor
        
        Args:
            connection_string: SQL Server connection string
            app_schema: Database schema name
            email_config: Email configuration dictionary
        """
        self.connection_string = connection_string
        self.app_schema = app_schema
        self.email_config = email_config or {}
        self.log_messages = []
        self.dependency_all = []
        
    def log(self, message: str):
        """Add message to log"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_messages.append(log_entry)
        arcpy.AddMessage(log_entry)
        
    def get_db_connection(self):
        """Create and return database connection"""
        try:
            conn = pyodbc.connect(self.connection_string)
            return conn
        except Exception as e:
            self.log(f"Error connecting to database: {str(e)}")
            raise
            
    def get_dependency_links_all(self, dependency_type: str) -> List[Dict]:
        """
        Get all dependency links from database
        
        Args:
            dependency_type: Either 'Depending' or 'Supporting'
            
        Returns:
            List of dependency mapping dictionaries
        """
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Determine table name based on type
            table_name = "INFRATAGGING_MAPPING MAPP" if dependency_type == "Depending" else "INFRATAGGING_MAPPING_SUPP_VW MAPP"
            
            # Build SQL query
            sql_query = f"""
            SET LOCK_TIMEOUT 10000;
            SET QUERY_GOVERNOR_COST_LIMIT 0;
            SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
            
            SELECT DISTINCT 
                MAPP.SOURCE_FEATUREID,
                MAPP.SOURCE_LAYERID,
                MAPP.DESTINATION_FEATUREID,
                MAPP.DESTINATION_LAYERID,
                SRC_LAYERS.LAYER_NAME AS SOURCELAYER,
                DEST_LAYERS.LAYER_NAME AS DESTINATIONLAYER,
                SRC_LAYERS.FEATURECLASS_NAME AS SOURCE_FEATURECLASS_NAME,
                DEST_LAYERS.FEATURECLASS_NAME AS DESTINATION_FEATURECLASS_NAME,
                SRC_STAGE.START_DATE AS SOURCE_START_DATE,
                SRC_STAGE.END_DATE AS SOURCE_END_DATE,
                DEST_STAGE.START_DATE AS DESTINATION_START_DATE,
                DEST_STAGE.END_DATE AS DESTINATION_END_DATE,
                COALESCE(SRC_STAGE.DESCRIPTION, SRC_LAYERS.LAYER_NAME + ' - ' + MAPP.SOURCE_FEATUREID) AS SOURCE_DESCRIPTION,
                COALESCE(DEST_STAGE.DESCRIPTION, DEST_LAYERS.LAYER_NAME + ' - ' + MAPP.DESTINATION_FEATUREID) AS DESTINATION_DESCRIPTION,
                MAPP.CREATEDDATE,
                MAPP.OFFICER
            FROM {self.app_schema}.{table_name}
            LEFT JOIN {self.app_schema}.INFRATAGGING_LAYERS_VW SRC_LAYERS
                ON SRC_LAYERS.LAYER_ID = MAPP.SOURCE_LAYERID
            LEFT JOIN {self.app_schema}.INFRATAGGING_LAYERS_VW DEST_LAYERS
                ON DEST_LAYERS.LAYER_ID = MAPP.DESTINATION_LAYERID
            LEFT JOIN {self.app_schema}.INFRA_CONS_STAGINGYR_VW SRC_STAGE
                ON SRC_STAGE.LAYER_ID = MAPP.SOURCE_LAYERID
                AND SRC_STAGE.FEATUREID = MAPP.SOURCE_FEATUREID
            LEFT JOIN {self.app_schema}.INFRA_CONS_STAGINGYR_VW DEST_STAGE
                ON DEST_STAGE.LAYER_ID = MAPP.DESTINATION_LAYERID
                AND DEST_STAGE.FEATUREID = MAPP.DESTINATION_FEATUREID
            """
            
            cursor.execute(sql_query)
            columns = [column[0] for column in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
                
            cursor.close()
            conn.close()
            
            return results
            
        except Exception as e:
            self.log(f"Error in get_dependency_links_all: {str(e)}")
            raise
            
    def get_infra_layers(self) -> List[Dict]:
        """Get infrastructure layer information from database"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            sql_query = f"""
            SELECT 
                infralayer.FEATURECLASS_NAME, 
                infralayer.LAYER_ID, 
                infralayer.LAYER_NAME, 
                infralayer.AGENCY 
            FROM {self.app_schema}.INFRATAGGING_LAYERS_VW infralayer
            """
            
            cursor.execute(sql_query)
            columns = [column[0] for column in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
                
            cursor.close()
            conn.close()
            
            return results
            
        except Exception as e:
            self.log(f"Error in get_infra_layers: {str(e)}")
            raise
            
    def filter_schedule_links(self, layer: str, feature_id: str, dependency_type: str, 
                             dependency_list: List[Dict] = None) -> Tuple[List[Dict], bool]:
        """
        Filter and process schedule links for a feature
        
        Args:
            layer: Layer name
            feature_id: Feature ID
            dependency_type: 'Depending' or 'Supporting'
            dependency_list: Pre-loaded dependency list (optional)
            
        Returns:
            Tuple of (schedule_data_list, has_issues)
        """
        schedule_data = []
        has_issues = False
        
        try:
            # Use provided list or get from database
            if dependency_list is None:
                dependency_list = self.dependency_all
                
            # Filter dependencies for this feature
            if dependency_type == "Depending":
                filtered = [d for d in dependency_list 
                          if d.get('SOURCELAYER') == layer and d.get('SOURCE_FEATUREID') == feature_id]
            else:
                filtered = [d for d in dependency_list 
                          if d.get('DESTINATIONLAYER') == layer and d.get('DESTINATION_FEATUREID') == feature_id]
                          
            # Process filtered dependencies
            for dep in filtered:
                if dependency_type == "Depending":
                    schedule_data.append({
                        'Name': dep.get('DESTINATIONLAYER', ''),
                        'SourceLayer': dep.get('SOURCELAYER', ''),
                        'Id': dep.get('DESTINATION_FEATUREID', ''),
                        'startDate': dep.get('DESTINATION_START_DATE'),
                        'endDate': dep.get('DESTINATION_END_DATE'),
                        'RelationId': 0,
                        'hasIssue': self.check_schedule_issue(dep)
                    })
                else:
                    schedule_data.append({
                        'Name': dep.get('SOURCELAYER', ''),
                        'SourceLayer': dep.get('DESTINATIONLAYER', ''),
                        'Id': dep.get('SOURCE_FEATUREID', ''),
                        'startDate': dep.get('SOURCE_START_DATE'),
                        'endDate': dep.get('SOURCE_END_DATE'),
                        'RelationId': 0,
                        'hasIssue': self.check_schedule_issue(dep)
                    })
                    
                if schedule_data[-1]['hasIssue']:
                    has_issues = True
                    
        except Exception as e:
            self.log(f"Error in filter_schedule_links: {str(e)}")
            
        return schedule_data, has_issues
        
    def check_schedule_issue(self, dependency: Dict) -> bool:
        """Check if there are scheduling issues between source and destination"""
        try:
            src_start = dependency.get('SOURCE_START_DATE')
            src_end = dependency.get('SOURCE_END_DATE')
            dest_start = dependency.get('DESTINATION_START_DATE')
            dest_end = dependency.get('DESTINATION_END_DATE')
            
            # Check for date conflicts or missing dates
            if not all([src_start, src_end, dest_start, dest_end]):
                return True
                
            # Convert to datetime if strings
            if isinstance(src_start, str):
                src_start = datetime.datetime.strptime(src_start[:10], '%Y-%m-%d')
            if isinstance(src_end, str):
                src_end = datetime.datetime.strptime(src_end[:10], '%Y-%m-%d')
            if isinstance(dest_start, str):
                dest_start = datetime.datetime.strptime(dest_start[:10], '%Y-%m-%d')
            if isinstance(dest_end, str):
                dest_end = datetime.datetime.strptime(dest_end[:10], '%Y-%m-%d')
                
            # Check if source ends after destination starts (potential issue)
            return src_end > dest_start
            
        except Exception:
            return False
            
    def process_infratagging_summary(self, dependency_type: str) -> List[Dict]:
        """
        Process infrastructure tagging summary for given type
        
        Args:
            dependency_type: Either 'Depending' or 'Supporting'
            
        Returns:
            List of infrastructure consumption features
        """
        try:
            self.log(f"Processing {dependency_type} features...")
            
            # Get dependency links
            self.dependency_all = self.get_dependency_links_all(dependency_type)
            self.log(f"Retrieved {len(self.dependency_all)} dependency links")
            
            # Get layer information
            layers = self.get_infra_layers()
            self.log(f"Retrieved {len(layers)} layers")
            
            # Create layer lookup dictionary
            layer_dict = {layer['LAYER_NAME']: layer for layer in layers}
            
            # Process each dependency
            infra_features = []
            type_id = 0 if dependency_type == "Depending" else 1
            
            for dep in self.dependency_all:
                source_layer = dep.get('SOURCELAYER', '')
                source_feature_id = dep.get('SOURCE_FEATUREID', '')
                
                # Filter schedule links
                schedule_data, has_issues = self.filter_schedule_links(
                    source_layer, source_feature_id, dependency_type, self.dependency_all
                )
                
                # Get matching layer
                matched_layer = layer_dict.get(source_layer)
                
                if matched_layer:
                    infra_features.append({
                        'Category': 1 if has_issues else 0,
                        'Type': type_id,
                        'FeatureId': source_feature_id,
                        'Layer_Id': matched_layer['LAYER_ID'],
                        'Layer': matched_layer['LAYER_NAME'],
                        'ChartJSON': None,
                        'ChartHeight': 0
                    })
                else:
                    infra_features.append({
                        'Category': 1 if has_issues else 0,
                        'Type': type_id,
                        'FeatureId': source_feature_id,
                        'Layer_Id': -1,
                        'Layer': f"Unknown Layer ({source_layer})",
                        'ChartJSON': None,
                        'ChartHeight': 0
                    })
                    
            # Remove duplicates
            unique_features = []
            seen = set()
            for feature in infra_features:
                key = (feature['FeatureId'], feature['Layer_Id'], feature['Type'])
                if key not in seen:
                    seen.add(key)
                    unique_features.append(feature)
                    
            self.log(f"Processed {len(unique_features)} unique {dependency_type} features")
            return unique_features
            
        except Exception as e:
            self.log(f"Error in process_infratagging_summary: {str(e)}")
            self.log(traceback.format_exc())
            raise
            
    def prepare_chart_json_data(self, island_wide_data: Dict) -> str:
        """
        Prepare chart JSON data for visualization
        
        Args:
            island_wide_data: Dictionary containing schedule data
            
        Returns:
            JSON string for chart rendering
        """
        try:
            schedule_data = island_wide_data.get('ScheduleData', [])
            
            # Prepare chart data structure
            chart_data = {
                'id': island_wide_data.get('Id', ''),
                'name': island_wide_data.get('Name', ''),
                'type': island_wide_data.get('Type', ''),
                'tasks': []
            }
            
            for idx, item in enumerate(schedule_data):
                task = {
                    'id': item.get('Id', ''),
                    'name': item.get('Name', ''),
                    'start': item.get('startDate', ''),
                    'end': item.get('endDate', ''),
                    'relationId': item.get('RelationId', 0),
                    'hasIssue': item.get('hasIssue', False)
                }
                chart_data['tasks'].append(task)
                
            return json.dumps(chart_data)
            
        except Exception as e:
            self.log(f"Error in prepare_chart_json_data: {str(e)}")
            return "{}"
            
    def get_chart_height(self, schedule_count: int) -> int:
        """Calculate chart height based on number of schedule items"""
        base_height = 100
        item_height = 30
        return base_height + (schedule_count * item_height)
        
    def get_schedule_data_island_wide(self, mapping_list: List[Dict], 
                                      dependency_type: str) -> List[Dict]:
        """
        Get schedule data for island-wide processing
        
        Args:
            mapping_list: List of infrastructure feature mappings
            dependency_type: 'Depending' or 'Supporting'
            
        Returns:
            List of island-wide schedule data with chart information
        """
        try:
            # Get all dependencies
            dependency_raw_all = self.get_dependency_links_all(dependency_type)
            
            island_wide_data = []
            
            for item in mapping_list:
                layer = item['Layer']
                feature_id = item['FeatureId']
                
                # Filter schedule links
                schedule_data, has_issues = self.filter_schedule_links(
                    layer, feature_id, dependency_type, dependency_raw_all
                )
                
                # Handle single item case
                if len(schedule_data) == 1:
                    filtered = [d for d in dependency_raw_all 
                              if d.get('DESTINATIONLAYER') == layer and 
                              d.get('DESTINATION_FEATUREID') == feature_id]
                    
                    if filtered:
                        schedule_data = [{
                            'Name': filtered[0].get('DESTINATIONLAYER', ''),
                            'Id': filtered[0].get('DESTINATION_FEATUREID', ''),
                            'startDate': filtered[0].get('DESTINATION_START_DATE'),
                            'endDate': filtered[0].get('DESTINATION_END_DATE'),
                            'RelationId': 1,
                            'hasIssue': False
                        }]
                        
                data_item = {
                    'Id': feature_id,
                    'ScheduleData': schedule_data,
                    'LayerId': int(item['Layer_Id']),
                    'Name': layer,
                    'Type': dependency_type
                }
                
                island_wide_data.append(data_item)
                
            # Generate chart data for each item
            for item in island_wide_data:
                item['ChartJSON'] = self.prepare_chart_json_data(item)
                item['ChartHeight'] = self.get_chart_height(len(item['ScheduleData']))
                
            return island_wide_data
            
        except Exception as e:
            self.log(f"Error in get_schedule_data_island_wide: {str(e)}")
            raise
            
    def add_to_summary_cache_results(self, lst_depending: List[Dict], 
                                    lst_supporting: List[Dict]):
        """
        Add processed results to summary cache table
        
        Args:
            lst_depending: List of depending features
            lst_supporting: List of supporting features
        """
        try:
            self.log("Generating chart data for Depending features...")
            depending_charts = self.get_schedule_data_island_wide(lst_depending, "Depending")
            
            self.log("Generating chart data for Supporting features...")
            supporting_charts = self.get_schedule_data_island_wide(lst_supporting, "Supporting")
            
            # Update depending features with chart data
            for feature in lst_depending:
                matching_charts = [c for c in depending_charts 
                                 if c['Id'] == feature['FeatureId'] and 
                                 c['LayerId'] == feature['Layer_Id']]
                if matching_charts:
                    feature['ChartJSON'] = matching_charts[0]['ChartJSON']
                    feature['ChartHeight'] = matching_charts[0]['ChartHeight']
                    
            # Update supporting features with chart data
            for feature in lst_supporting:
                matching_charts = [c for c in supporting_charts 
                                 if c['Id'] == feature['FeatureId'] and 
                                 c['LayerId'] == feature['Layer_Id']]
                if matching_charts:
                    feature['ChartJSON'] = matching_charts[0]['ChartJSON']
                    feature['ChartHeight'] = matching_charts[0]['ChartHeight']
                    
            # Save to database
            self.save_to_cache_table(lst_depending, lst_supporting)
            
        except Exception as e:
            self.log(f"Error in add_to_summary_cache_results: {str(e)}")
            raise
            
    def save_to_cache_table(self, lst_depending: List[Dict], lst_supporting: List[Dict]):
        """
        Save results to cache table in database
        
        Args:
            lst_depending: List of depending features
            lst_supporting: List of supporting features
        """
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Clear existing cache
            clear_sql = f"DELETE FROM {self.app_schema}.INFRATAGGING_SUMMARY_CACHE"
            cursor.execute(clear_sql)
            
            # Insert depending features
            insert_sql = f"""
            INSERT INTO {self.app_schema}.INFRATAGGING_SUMMARY_CACHE 
            (FEATUREID, LAYER_ID, LAYER_NAME, TYPE, CATEGORY, CHART_JSON, CHART_HEIGHT, CREATED_DATE)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            current_time = datetime.datetime.now()
            
            for feature in lst_depending:
                cursor.execute(insert_sql, (
                    feature['FeatureId'],
                    feature['Layer_Id'],
                    feature['Layer'],
                    feature['Type'],
                    feature['Category'],
                    feature.get('ChartJSON'),
                    feature.get('ChartHeight', 0),
                    current_time
                ))
                
            # Insert supporting features
            for feature in lst_supporting:
                cursor.execute(insert_sql, (
                    feature['FeatureId'],
                    feature['Layer_Id'],
                    feature['Layer'],
                    feature['Type'],
                    feature['Category'],
                    feature.get('ChartJSON'),
                    feature.get('ChartHeight', 0),
                    current_time
                ))
                
            conn.commit()
            cursor.close()
            conn.close()
            
            self.log(f"Successfully saved {len(lst_depending) + len(lst_supporting)} records to cache")
            
        except Exception as e:
            self.log(f"Error in save_to_cache_table: {str(e)}")
            raise
            
    def send_status_email(self, status: str):
        """
        Send status email notification
        
        Args:
            status: Status message ('Success' or 'Failed')
        """
        try:
            if not self.email_config:
                self.log("Email configuration not provided, skipping email notification")
                return
                
            smtp_server = self.email_config.get('smtp_server')
            smtp_port = self.email_config.get('smtp_port', 587)
            from_email = self.email_config.get('from_email')
            to_emails = self.email_config.get('to_emails', [])
            username = self.email_config.get('username')
            password = self.email_config.get('password')
            
            if not all([smtp_server, from_email, to_emails]):
                self.log("Incomplete email configuration, skipping notification")
                return
                
            # Create message
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = ', '.join(to_emails) if isinstance(to_emails, list) else to_emails
            msg['Subject'] = f"Infratagging Summary Generation - {status}"
            
            # Email body
            body = f"""
            Infratagging Summary Generation Status: {status}
            
            Execution Time: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            
            Logs:
            {''.join(self.log_messages)}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                if username and password:
                    server.login(username, password)
                server.send_message(msg)
                
            self.log("Status email sent successfully")
            
        except Exception as e:
            self.log(f"Error sending status email: {str(e)}")
            
    def execute(self) -> str:
        """
        Main execution method
        
        Returns:
            Status string ('Success' or 'Failed')
        """
        status = "Failed"
        
        try:
            self.log("="*80)
            self.log("Started Infratagging Summary Generation Job")
            self.log("="*80)
            
            # Process depending features
            self.log("Executing for Depending Features")
            lst_depending = self.process_infratagging_summary("Depending")
            self.log(f"Depending Features execution completed. Total Count: {len(lst_depending)}")
            
            # Process supporting features
            self.log("Executing for Supporting Features")
            lst_supporting = self.process_infratagging_summary("Supporting")
            self.log(f"Supporting Features execution completed. Total Count: {len(lst_supporting)}")
            
            # Update cache table
            self.log("Updating Infratagging Cache table")
            self.add_to_summary_cache_results(lst_depending, lst_supporting)
            self.log("Update successful to Infratagging Cache table")
            
            status = "Success"
            self.log("="*80)
            
        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            self.log(traceback.format_exc())
            status = "Failed"
            
        finally:
            # Send status email
            self.send_status_email(status)
            
        return status


def main():
    """
    Main function for ArcGIS Geoprocessing Tool
    """
    try:
        # Get parameters from GP tool
        connection_string = arcpy.GetParameterAsText(0)  # SQL Server connection string
        app_schema = arcpy.GetParameterAsText(1)  # Database schema name
        
        # Optional email parameters
        smtp_server = arcpy.GetParameterAsText(2)  # SMTP server
        smtp_port = arcpy.GetParameter(3) if arcpy.GetParameterAsText(3) else 587  # SMTP port
        from_email = arcpy.GetParameterAsText(4)  # From email address
        to_emails = arcpy.GetParameterAsText(5)  # To email addresses (comma-separated)
        email_username = arcpy.GetParameterAsText(6)  # Email username (optional)
        email_password = arcpy.GetParameterAsText(7)  # Email password (optional)
        
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
        
        # Create processor instance
        processor = InfraTaggingProcessor(connection_string, app_schema, email_config)
        
        # Execute processing
        status = processor.execute()
        
        # Set output parameter
        arcpy.SetParameterAsText(8, status)
        
        if status == "Success":
            arcpy.AddMessage("Job completed successfully!")
        else:
            arcpy.AddError("Job failed. Check logs for details.")
            
    except Exception as e:
        arcpy.AddError(f"Fatal error: {str(e)}")
        arcpy.AddError(traceback.format_exc())
        arcpy.SetParameterAsText(8, "Failed")


if __name__ == "__main__":
    main()
