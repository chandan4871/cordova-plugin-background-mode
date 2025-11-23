"""
========================================================================
Infrastructure Tagging Summary Generation - Single File Version
========================================================================
This script processes infrastructure tagging summaries for Depending 
and Supporting features and caches results with chart data.

Usage:
    python infratagging_summary.py

Edit the CONFIGURATION section below with your settings.
========================================================================
"""

import sys
import time
import json
import logging
import os
import datetime
import traceback
from typing import List, Dict, Tuple
import arcpy
from arcpy import da
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# ========================================================================
# CONFIGURATION - EDIT THESE SETTINGS
# ========================================================================

# Database Connection
SDE_PATH = r"C:\temp\SDE_Conn\ONETOOLDEV_ONETOOL_ARCGIS_CONN_SQL.sde"
APP_SCHEMA = "ONETOOLAPP."  # Must include trailing dot!

# Logging
LOG_FOLDER = r"C:\temp\GPLogs"
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR

# Email Notifications (Set ENABLE_EMAIL = False to disable)
ENABLE_EMAIL = True
SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587
FROM_EMAIL = "noreply@your-company.com"
TO_EMAILS = ["admin@your-company.com", "team@your-company.com"]
EMAIL_USERNAME = "noreply@your-company.com"  # Leave empty if not needed
EMAIL_PASSWORD = "your_password"  # Leave empty if not needed

# Processing Options
BATCH_SIZE = 100  # Records per batch for INSERT operations

# ========================================================================
# END CONFIGURATION
# ========================================================================


class InfraTaggingProcessor:
    """Main processor class for infrastructure tagging summary generation"""
    
    def __init__(self):
        """Initialize the processor with configuration"""
        self.sde_path = SDE_PATH
        self.app_schema = APP_SCHEMA
        self.log_messages = []
        self.dependency_all = []
        
        # Setup logging
        self._setup_logging()
        
        # Initialize SDE connection
        try:
            self.db_conn = arcpy.ArcSDESQLExecute(self.sde_path)
            self.log("SDE connection initialized successfully")
        except Exception as e:
            self.log(f"Error initializing SDE connection: {str(e)}")
            raise
    
    def _setup_logging(self):
        """Setup logging configuration"""
        if not os.path.exists(LOG_FOLDER):
            os.makedirs(LOG_FOLDER)
        
        log_file = time.strftime("%Y%m%d") + "_InfraTaggingSummary.log"
        logging.basicConfig(
            filename=os.path.join(LOG_FOLDER, log_file),
            format='%(asctime)s - %(levelname)s - %(message)s',
            level=getattr(logging, LOG_LEVEL)
        )
    
    def log(self, message: str):
        """Add message to log"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_messages.append(log_entry)
        print(log_entry)  # Also print to console
        logging.info(message)
    
    def execute_sql(self, sql: str):
        """Execute SQL against ArcGIS SDE"""
        try:
            sde = arcpy.ArcSDESQLExecute(self.sde_path)
            result = sde.execute(sql)
            
            if result == True:
                return result
            elif isinstance(result, list):
                return result
            else:
                self.log(f"SQL execution returned: {result}")
                return result
        except Exception as ex:
            self.log(f"SQL execution failed: {str(ex)}")
            raise
    
    def get_dependency_links_all(self, dependency_type: str) -> List[Dict]:
        """Get all dependency links from database"""
        try:
            table_name = "INFRATAGGING_MAPPING MAPP" if dependency_type == "Depending" else "INFRATAGGING_MAPPING_SUPP_VW MAPP"
            
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
            FROM {self.app_schema}{table_name}
            LEFT JOIN {self.app_schema}INFRATAGGING_LAYERS_VW SRC_LAYERS
                ON SRC_LAYERS.LAYER_ID = MAPP.SOURCE_LAYERID
            LEFT JOIN {self.app_schema}INFRATAGGING_LAYERS_VW DEST_LAYERS
                ON DEST_LAYERS.LAYER_ID = MAPP.DESTINATION_LAYERID
            LEFT JOIN {self.app_schema}INFRA_CONS_STAGINGYR_VW SRC_STAGE
                ON SRC_STAGE.LAYER_ID = MAPP.SOURCE_LAYERID
                AND SRC_STAGE.FEATUREID = MAPP.SOURCE_FEATUREID
            LEFT JOIN {self.app_schema}INFRA_CONS_STAGINGYR_VW DEST_STAGE
                ON DEST_STAGE.LAYER_ID = MAPP.DESTINATION_LAYERID
                AND DEST_STAGE.FEATUREID = MAPP.DESTINATION_FEATUREID
            """
            
            result = self.execute_sql(sql_query)
            
            if not result or result == True:
                return []
            
            columns = [
                'SOURCE_FEATUREID', 'SOURCE_LAYERID', 'DESTINATION_FEATUREID', 
                'DESTINATION_LAYERID', 'SOURCELAYER', 'DESTINATIONLAYER',
                'SOURCE_FEATURECLASS_NAME', 'DESTINATION_FEATURECLASS_NAME',
                'SOURCE_START_DATE', 'SOURCE_END_DATE', 
                'DESTINATION_START_DATE', 'DESTINATION_END_DATE',
                'SOURCE_DESCRIPTION', 'DESTINATION_DESCRIPTION',
                'CREATEDDATE', 'OFFICER'
            ]
            
            results = []
            for row in result:
                results.append(dict(zip(columns, row)))
            
            return results
        except Exception as e:
            self.log(f"Error in get_dependency_links_all: {str(e)}")
            raise
    
    def get_infra_layers(self) -> List[Dict]:
        """Get infrastructure layer information"""
        try:
            sql_query = f"""
            SELECT 
                infralayer.FEATURECLASS_NAME, 
                infralayer.LAYER_ID, 
                infralayer.LAYER_NAME, 
                infralayer.AGENCY 
            FROM {self.app_schema}INFRATAGGING_LAYERS_VW infralayer
            """
            
            result = self.execute_sql(sql_query)
            
            if not result or result == True:
                return []
            
            columns = ['FEATURECLASS_NAME', 'LAYER_ID', 'LAYER_NAME', 'AGENCY']
            results = []
            
            for row in result:
                results.append(dict(zip(columns, row)))
            
            return results
        except Exception as e:
            self.log(f"Error in get_infra_layers: {str(e)}")
            raise
    
    def filter_schedule_links(self, layer: str, feature_id: str, dependency_type: str, 
                             dependency_list: List[Dict] = None) -> Tuple[List[Dict], bool]:
        """Filter and process schedule links for a feature"""
        schedule_data = []
        has_issues = False
        
        try:
            if dependency_list is None:
                dependency_list = self.dependency_all
            
            if dependency_type == "Depending":
                filtered = [d for d in dependency_list 
                          if d.get('SOURCELAYER') == layer and str(d.get('SOURCE_FEATUREID')) == str(feature_id)]
            else:
                filtered = [d for d in dependency_list 
                          if d.get('DESTINATIONLAYER') == layer and str(d.get('DESTINATION_FEATUREID')) == str(feature_id)]
            
            for dep in filtered:
                if dependency_type == "Depending":
                    schedule_data.append({
                        'Name': dep.get('DESTINATIONLAYER', ''),
                        'SourceLayer': dep.get('SOURCELAYER', ''),
                        'Id': str(dep.get('DESTINATION_FEATUREID', '')),
                        'startDate': self.format_date(dep.get('DESTINATION_START_DATE')),
                        'endDate': self.format_date(dep.get('DESTINATION_END_DATE')),
                        'RelationId': 0,
                        'hasIssue': self.check_schedule_issue(dep)
                    })
                else:
                    schedule_data.append({
                        'Name': dep.get('SOURCELAYER', ''),
                        'SourceLayer': dep.get('DESTINATIONLAYER', ''),
                        'Id': str(dep.get('SOURCE_FEATUREID', '')),
                        'startDate': self.format_date(dep.get('SOURCE_START_DATE')),
                        'endDate': self.format_date(dep.get('SOURCE_END_DATE')),
                        'RelationId': 0,
                        'hasIssue': self.check_schedule_issue(dep)
                    })
                
                if schedule_data[-1]['hasIssue']:
                    has_issues = True
        except Exception as e:
            self.log(f"Error in filter_schedule_links: {str(e)}")
        
        return schedule_data, has_issues
    
    def format_date(self, date_val):
        """Format date value to string"""
        if date_val is None:
            return None
        if isinstance(date_val, datetime.datetime):
            return date_val.strftime('%Y-%m-%d')
        if isinstance(date_val, str):
            return date_val[:10] if len(date_val) >= 10 else date_val
        return str(date_val)
    
    def check_schedule_issue(self, dependency: Dict) -> bool:
        """Check if there are scheduling issues"""
        try:
            src_start = dependency.get('SOURCE_START_DATE')
            src_end = dependency.get('SOURCE_END_DATE')
            dest_start = dependency.get('DESTINATION_START_DATE')
            dest_end = dependency.get('DESTINATION_END_DATE')
            
            if not all([src_start, src_end, dest_start, dest_end]):
                return True
            
            if isinstance(src_start, str):
                src_start = datetime.datetime.strptime(src_start[:10], '%Y-%m-%d')
            if isinstance(src_end, str):
                src_end = datetime.datetime.strptime(src_end[:10], '%Y-%m-%d')
            if isinstance(dest_start, str):
                dest_start = datetime.datetime.strptime(dest_start[:10], '%Y-%m-%d')
            if isinstance(dest_end, str):
                dest_end = datetime.datetime.strptime(dest_end[:10], '%Y-%m-%d')
            
            return src_end > dest_start
        except Exception:
            return False
    
    def process_infratagging_summary(self, dependency_type: str) -> List[Dict]:
        """Process infrastructure tagging summary for given type"""
        try:
            self.log(f"Processing {dependency_type} features...")
            
            self.dependency_all = self.get_dependency_links_all(dependency_type)
            self.log(f"Retrieved {len(self.dependency_all)} dependency links")
            
            layers = self.get_infra_layers()
            self.log(f"Retrieved {len(layers)} layers")
            
            layer_dict = {layer['LAYER_NAME']: layer for layer in layers}
            
            infra_features = []
            type_id = 0 if dependency_type == "Depending" else 1
            
            for dep in self.dependency_all:
                source_layer = dep.get('SOURCELAYER', '')
                source_feature_id = str(dep.get('SOURCE_FEATUREID', ''))
                
                schedule_data, has_issues = self.filter_schedule_links(
                    source_layer, source_feature_id, dependency_type, self.dependency_all
                )
                
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
        """Prepare chart JSON data for visualization"""
        try:
            schedule_data = island_wide_data.get('ScheduleData', [])
            
            chart_data = {
                'id': island_wide_data.get('Id', ''),
                'name': island_wide_data.get('Name', ''),
                'type': island_wide_data.get('Type', ''),
                'tasks': []
            }
            
            for item in schedule_data:
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
        """Get schedule data for island-wide processing"""
        try:
            dependency_raw_all = self.get_dependency_links_all(dependency_type)
            
            island_wide_data = []
            
            for item in mapping_list:
                layer = item['Layer']
                feature_id = str(item['FeatureId'])
                
                schedule_data, has_issues = self.filter_schedule_links(
                    layer, feature_id, dependency_type, dependency_raw_all
                )
                
                if len(schedule_data) == 1:
                    filtered = [d for d in dependency_raw_all 
                              if d.get('DESTINATIONLAYER') == layer and 
                              str(d.get('DESTINATION_FEATUREID')) == feature_id]
                    
                    if filtered:
                        schedule_data = [{
                            'Name': filtered[0].get('DESTINATIONLAYER', ''),
                            'Id': str(filtered[0].get('DESTINATION_FEATUREID', '')),
                            'startDate': self.format_date(filtered[0].get('DESTINATION_START_DATE')),
                            'endDate': self.format_date(filtered[0].get('DESTINATION_END_DATE')),
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
            
            for item in island_wide_data:
                item['ChartJSON'] = self.prepare_chart_json_data(item)
                item['ChartHeight'] = self.get_chart_height(len(item['ScheduleData']))
            
            return island_wide_data
        except Exception as e:
            self.log(f"Error in get_schedule_data_island_wide: {str(e)}")
            raise
    
    def add_to_summary_cache_results(self, lst_depending: List[Dict], 
                                    lst_supporting: List[Dict]):
        """Add processed results to summary cache table"""
        try:
            self.log("Generating chart data for Depending features...")
            depending_charts = self.get_schedule_data_island_wide(lst_depending, "Depending")
            
            self.log("Generating chart data for Supporting features...")
            supporting_charts = self.get_schedule_data_island_wide(lst_supporting, "Supporting")
            
            for feature in lst_depending:
                matching_charts = [c for c in depending_charts 
                                 if str(c['Id']) == str(feature['FeatureId']) and 
                                 c['LayerId'] == feature['Layer_Id']]
                if matching_charts:
                    feature['ChartJSON'] = matching_charts[0]['ChartJSON']
                    feature['ChartHeight'] = matching_charts[0]['ChartHeight']
            
            for feature in lst_supporting:
                matching_charts = [c for c in supporting_charts 
                                 if str(c['Id']) == str(feature['FeatureId']) and 
                                 c['LayerId'] == feature['Layer_Id']]
                if matching_charts:
                    feature['ChartJSON'] = matching_charts[0]['ChartJSON']
                    feature['ChartHeight'] = matching_charts[0]['ChartHeight']
            
            self.save_to_cache_table(lst_depending, lst_supporting)
        except Exception as e:
            self.log(f"Error in add_to_summary_cache_results: {str(e)}")
            raise
    
    def save_to_cache_table(self, lst_depending: List[Dict], lst_supporting: List[Dict]):
        """Save results to cache table in database"""
        try:
            clear_sql = f"DELETE FROM {self.app_schema}INFRATAGGING_SUMMARY_CACHE"
            self.execute_sql(clear_sql)
            self.log("Cleared existing cache data")
            
            all_features = lst_depending + lst_supporting
            
            total_inserted = 0
            for i in range(0, len(all_features), BATCH_SIZE):
                batch = all_features[i:i + BATCH_SIZE]
                
                values_list = []
                for feature in batch:
                    feature_id = str(feature['FeatureId']).replace("'", "''")
                    layer_name = str(feature['Layer']).replace("'", "''")
                    chart_json = str(feature.get('ChartJSON', '')).replace("'", "''") if feature.get('ChartJSON') else ''
                    
                    values = f"('{feature_id}', {feature['Layer_Id']}, '{layer_name}', {feature['Type']}, {feature['Category']}, '{chart_json}', {feature.get('ChartHeight', 0)}, GETDATE())"
                    values_list.append(values)
                
                insert_sql = f"""
                INSERT INTO {self.app_schema}INFRATAGGING_SUMMARY_CACHE 
                (FEATUREID, LAYER_ID, LAYER_NAME, TYPE, CATEGORY, CHART_JSON, CHART_HEIGHT, CREATED_DATE)
                VALUES {','.join(values_list)}
                """
                
                self.execute_sql(insert_sql)
                total_inserted += len(batch)
            
            self.log(f"Successfully saved {total_inserted} records to cache table")
        except Exception as e:
            self.log(f"Error in save_to_cache_table: {str(e)}")
            raise
    
    def send_status_email(self, status: str):
        """Send status email notification"""
        try:
            if not ENABLE_EMAIL:
                self.log("Email notifications disabled")
                return
            
            if not all([SMTP_SERVER, FROM_EMAIL, TO_EMAILS]):
                self.log("Incomplete email configuration, skipping notification")
                return
            
            msg = MIMEMultipart()
            msg['From'] = FROM_EMAIL
            msg['To'] = ', '.join(TO_EMAILS) if isinstance(TO_EMAILS, list) else TO_EMAILS
            msg['Subject'] = f"Infratagging Summary Generation - {status}"
            
            body = f"""
            Infratagging Summary Generation Status: {status}
            
            Execution Time: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            
            Logs:
            {chr(10).join(self.log_messages)}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                if EMAIL_USERNAME and EMAIL_PASSWORD:
                    server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
                server.send_message(msg)
            
            self.log("Status email sent successfully")
        except Exception as e:
            self.log(f"Error sending status email: {str(e)}")
    
    def execute(self) -> str:
        """Main execution method"""
        status = "Failed"
        
        try:
            self.log("="*80)
            self.log("Started Infratagging Summary Generation Job")
            self.log("="*80)
            
            self.log("Executing for Depending Features")
            lst_depending = self.process_infratagging_summary("Depending")
            self.log(f"Depending Features execution completed. Total Count: {len(lst_depending)}")
            
            self.log("Executing for Supporting Features")
            lst_supporting = self.process_infratagging_summary("Supporting")
            self.log(f"Supporting Features execution completed. Total Count: {len(lst_supporting)}")
            
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
            self.send_status_email(status)
        
        return status


# ========================================================================
# MAIN EXECUTION
# ========================================================================

def main():
    """Main function"""
    try:
        print("="*80)
        print("Infrastructure Tagging Summary Generation")
        print("="*80)
        print(f"SDE Path: {SDE_PATH}")
        print(f"Schema: {APP_SCHEMA}")
        print(f"Log Folder: {LOG_FOLDER}")
        print(f"Email Notifications: {'Enabled' if ENABLE_EMAIL else 'Disabled'}")
        print("="*80)
        print()
        
        processor = InfraTaggingProcessor()
        status = processor.execute()
        
        print()
        print("="*80)
        if status == "Success":
            print("✓ Job completed successfully!")
            print("="*80)
            return 0
        else:
            print("✗ Job failed. Check logs for details.")
            print("="*80)
            return 1
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
