#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Infrastructure Tagging Summary Generation Script
Processes infrastructure dependencies and generates summary cache for ArcGIS.
"""

import arcpy
import datetime
import json
import logging
import os
import sys
import time
import traceback
from typing import List, Dict

# ========================================================================
# CONFIGURATION - Update these values for your environment
# ========================================================================
SDE_PATH = arcpy.GetParameterAsText(0) if arcpy.GetParameterAsText(0) else r"Database Connections\YourConnection.sde"
APP_SCHEMA = "YOUR_SCHEMA."  # Update with your schema name
LOG_FOLDER = r"C:\Logs\InfraTagging"  # Update with your log folder path
LOG_LEVEL = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR

# ========================================================================
# MAIN PROCESSOR CLASS
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
            self.log(f"Error initializing SDE connection: {str(e)}", "ERROR")
            raise
    
    def _setup_logging(self):
        """Setup logging configuration"""
        try:
            if not os.path.exists(LOG_FOLDER):
                os.makedirs(LOG_FOLDER)
                arcpy.AddMessage(f"Created log folder: {LOG_FOLDER}")
            
            log_file = time.strftime("%Y%m%d") + "_GenerateInfrataggingSummaryIslandWide.log"
            self.log_file_path = os.path.join(LOG_FOLDER, log_file)
            
            # Remove existing handlers to force reconfiguration (compatible with older Python)
            for handler in logging.root.handlers[:]:
                logging.root.removeHandler(handler)
            
            logging.basicConfig(
                filename=self.log_file_path,
                format='%(asctime)s - %(levelname)s - %(message)s',
                level=getattr(logging, LOG_LEVEL)
            )
            
            arcpy.AddMessage(f"Log file: {self.log_file_path}")
        except Exception as e:
            arcpy.AddError(f"Error setting up logging: {str(e)}")
            # Continue even if logging fails
            self.log_file_path = None
    
    def log(self, message: str, message_type: str = "INFO"):
        """
        Add message to log and ArcGIS messages.
        message_type: INFO, WARNING, ERROR
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_messages.append(log_entry)
        
        # ALWAYS call arcpy.AddMessage FIRST (like working script)
        if message_type == "ERROR":
            arcpy.AddError(message)
        elif message_type == "WARNING":
            arcpy.AddWarning(message)
        else:
            arcpy.AddMessage(message)
        
        # Then log to file
        try:
            if message_type == "ERROR":
                logging.error(message)
            elif message_type == "WARNING":
                logging.warning(message)
            else:
                logging.info(message)
        except UnicodeEncodeError:
            # Fallback: remove non-ASCII characters if encoding fails
            ascii_message = message.encode('ascii', 'replace').decode('ascii')
            if message_type == "ERROR":
                logging.error(ascii_message)
            elif message_type == "WARNING":
                logging.warning(ascii_message)
            else:
                logging.info(ascii_message)
        
        # Finally print to console
        try:
            print(log_entry)
        except UnicodeEncodeError:
            # Fallback for console output
            ascii_log_entry = log_entry.encode('ascii', 'replace').decode('ascii')
            print(ascii_log_entry)
        sys.stdout.flush()
    
    def execute_sql_query(self, table_name: str, where_clause: str = "") -> List:
        """Execute SQL query using SearchCursor for better reliability"""
        try:
            full_table_path = os.path.join(self.sde_path, table_name)
            
            if not arcpy.Exists(full_table_path):
                self.log(f"Table does not exist: {full_table_path}", "ERROR")
                return []
            
            results = []
            with arcpy.da.SearchCursor(full_table_path, "*", where_clause) as cursor:
                field_names = cursor.fields
                
                for row in cursor:
                    row_dict = {}
                    for i, field_name in enumerate(field_names):
                        row_dict[field_name] = row[i]
                    results.append(row_dict)
            
            return results
        except Exception as e:
            self.log(f"Error in execute_sql_query for {table_name}: {str(e)}", "ERROR")
            return []
    
    def execute_sql_direct(self, sql: str):
        """Execute SQL statement directly (for INSERT/UPDATE/DELETE)"""
        try:
            sde = arcpy.ArcSDESQLExecute(self.sde_path)
            result = sde.execute(sql)
            return result
        except Exception as ex:
            self.log(f"SQL execution failed: {str(ex)}", "ERROR")
            raise
    
    def get_dependency_links_all(self, dependency_type: str) -> List[Dict]:
        """Get all dependency links from database using SearchCursor"""
        try:
            if dependency_type == "Depending":
                table_name = self.app_schema.rstrip('.') + ".INFRATAGGING_MAPPING"
            else:
                table_name = self.app_schema.rstrip('.') + ".INFRATAGGING_MAPPING_SUPP_VW"
            
            self.log(f"Querying table: {table_name}")
            arcpy.AddMessage(f"Querying table: {table_name}")
            
            mapping_records = self.execute_sql_query(table_name)
            self.log(f"Retrieved {len(mapping_records)} mapping records")
            arcpy.AddMessage(f"Retrieved {len(mapping_records)} mapping records")
            
            layers_table = self.app_schema.rstrip('.') + ".INFRATAGGING_LAYERS_VW"
            layer_records = self.execute_sql_query(layers_table)
            layer_dict = {}
            for layer in layer_records:
                layer_id = layer.get('LAYER_ID')
                if layer_id:
                    # Convert to string for consistent matching
                    layer_dict[str(layer_id)] = layer
            
            self.log(f"Retrieved {len(layer_dict)} layer records")
            arcpy.AddMessage(f"Retrieved {len(layer_dict)} layer records")
            
            staging_table = self.app_schema.rstrip('.') + ".INFRA_CONS_STAGINGYR_VW"
            staging_records = self.execute_sql_query(staging_table)
            staging_dict = {}
            for stage in staging_records:
                layer_id = stage.get('LAYER_ID')
                feature_id = stage.get('FEATUREID')
                if layer_id and feature_id:
                    # Convert layer_id to string for consistent matching
                    key = (str(layer_id), str(feature_id))
                    staging_dict[key] = stage
            
            self.log(f"Retrieved {len(staging_dict)} staging records")
            arcpy.AddMessage(f"Retrieved {len(staging_dict)} staging records")
            
            results = []
            seen_keys = set()
            
            for mapping in mapping_records:
                source_layer_id = mapping.get('SOURCE_LAYERID')
                source_feature_id = str(mapping.get('SOURCE_FEATUREID', ''))
                dest_layer_id = mapping.get('DESTINATION_LAYERID')
                dest_feature_id = str(mapping.get('DESTINATION_FEATUREID', ''))
                
                unique_key = (source_feature_id, source_layer_id, dest_feature_id, dest_layer_id)
                if unique_key in seen_keys:
                    continue
                seen_keys.add(unique_key)
                
                # Use string keys for lookups
                src_layer = layer_dict.get(str(source_layer_id), {})
                dest_layer = layer_dict.get(str(dest_layer_id), {})
                src_stage = staging_dict.get((str(source_layer_id), source_feature_id), {})
                dest_stage = staging_dict.get((str(dest_layer_id), dest_feature_id), {})
                
                # Build SOURCE_DESCRIPTION and DESTINATION_DESCRIPTION
                # COALESCE(DESCRIPTION, LAYER_NAME + ' - ' + FEATUREID)
                src_description = src_stage.get('DESCRIPTION') if src_stage.get('DESCRIPTION') else f"{src_layer.get('LAYER_NAME', '')} - {source_feature_id}"
                dest_description = dest_stage.get('DESCRIPTION') if dest_stage.get('DESCRIPTION') else f"{dest_layer.get('LAYER_NAME', '')} - {dest_feature_id}"
                
                result = {
                    'SOURCE_FEATUREID': source_feature_id,
                    'SOURCE_LAYERID': source_layer_id,
                    'DESTINATION_FEATUREID': dest_feature_id,
                    'DESTINATION_LAYERID': dest_layer_id,
                    'SOURCELAYER': src_layer.get('LAYER_NAME', ''),
                    'DESTINATIONLAYER': dest_layer.get('LAYER_NAME', ''),
                    'SOURCE_START_DATE': src_stage.get('START_DATE'),
                    'SOURCE_END_DATE': src_stage.get('END_DATE'),
                    'DESTINATION_START_DATE': dest_stage.get('START_DATE'),
                    'DESTINATION_END_DATE': dest_stage.get('END_DATE'),
                    'SOURCE_DESCRIPTION': src_description,
                    'DESTINATION_DESCRIPTION': dest_description,
                    'CREATEDDATE': mapping.get('CREATEDDATE'),
                    'OFFICER': mapping.get('OFFICER')
                }
                
                results.append(result)
            
            self.log(f"Built {len(results)} dependency link records")
            arcpy.AddMessage(f"Built {len(results)} dependency link records")
            return results
            
        except Exception as e:
            self.log(f"Error in get_dependency_links_all: {str(e)}", "ERROR")
            raise
    
    def get_infra_layers(self) -> List[Dict]:
        """Get infrastructure layer information"""
        try:
            table_name = self.app_schema.rstrip('.') + ".INFRATAGGING_LAYERS_VW"
            results = self.execute_sql_query(table_name)
            return results
        except Exception as e:
            self.log(f"Error in get_infra_layers: {str(e)}", "ERROR")
            raise
    
    def filter_schedule_links(self, source_layer: str, source_feature: str, 
                             start_date: str, end_date: str, description: str,
                             schedule_data_list: List[Dict], has_issues_ref: List[bool],
                             rel_id: int, dependency_type: str, 
                             dependency_list: List[Dict]) -> int:
        """
        RECURSIVE function to filter and process schedule links for a feature.
        Builds a complete dependency tree by following all links.
        """
        try:
            # Filter dependencies where SOURCELAYER matches
            filtered = [d for d in dependency_list 
                       if d.get('SOURCELAYER') == source_layer and 
                       str(d.get('SOURCE_FEATUREID')) == str(source_feature)]
            
            rel_id += 1
            
            if len(filtered) > 0:
                for dep in filtered:
                    # Add schedule data for this dependency (use DESTINATION data!)
                    schedule_item = {
                        'Name': dep.get('DESTINATION_DESCRIPTION', ''),
                        'SourceLayer': dep.get('DESTINATIONLAYER', ''),
                        'Id': str(dep.get('DESTINATION_FEATUREID', '')),
                        'startDate': self.format_date(dep.get('DESTINATION_START_DATE')),
                        'endDate': self.format_date(dep.get('DESTINATION_END_DATE')),
                        'RelationId': rel_id,
                        'hasIssue': False
                    }
                    
                    # Check for scheduling issues
                    if dependency_type == "Depending":
                        # For Depending: issue if destination ends AFTER source starts
                        dest_end = self.convert_to_int(dep.get('DESTINATION_END_DATE'))
                        src_end = self.convert_to_int(dep.get('SOURCE_END_DATE'))
                        if dest_end > src_end:
                            has_issues_ref[0] = True
                            schedule_item['hasIssue'] = True
                    else:
                        # For Supporting: issue if destination ends BEFORE source ends
                        dest_end = self.convert_to_int(dep.get('DESTINATION_END_DATE'))
                        src_end = self.convert_to_int(dep.get('SOURCE_END_DATE'))
                        if dest_end < src_end:
                            has_issues_ref[0] = True
                            schedule_item['hasIssue'] = True
                    
                    schedule_data_list.append(schedule_item)
                    
                    # Check for circular reference
                    dest_layer = dep.get('DESTINATIONLAYER', '')
                    dest_feature = str(dep.get('DESTINATION_FEATUREID', ''))
                    
                    is_circular = any(
                        s.get('SourceLayer') == dest_layer and 
                        str(s.get('Id')) == dest_feature 
                        for s in schedule_data_list
                    )
                    
                    if not is_circular:
                        # RECURSIVE CALL - continue from destination (becomes new source)
                        rel_id = self.filter_schedule_links(
                            dest_layer,  # This becomes the new source layer
                            dest_feature,  # This becomes the new source feature
                            dep.get('DESTINATION_START_DATE', ''),
                            dep.get('DESTINATION_END_DATE', ''),
                            dep.get('DESTINATION_DESCRIPTION', ''),
                            schedule_data_list,
                            has_issues_ref,
                            rel_id,
                            dependency_type,
                            dependency_list
                        )
            else:
                # No dependencies found - add leaf node
                schedule_data_list.append({
                    'Name': description,
                    'SourceLayer': source_layer,
                    'Id': source_feature,
                    'startDate': start_date,
                    'endDate': end_date,
                    'RelationId': rel_id,
                    'hasIssue': False
                })
            
            return rel_id
            
        except Exception as e:
            self.log(f"Error in filter_schedule_links: {str(e)}", "ERROR")
            return rel_id
    
    def format_date(self, date_val):
        """Format date value to string (YYYY format for charts)"""
        if date_val is None:
            return None
        if isinstance(date_val, datetime.datetime):
            return str(date_val.year)  # Return year only for chart
        if isinstance(date_val, str):
            # Extract year from date string
            try:
                if len(date_val) >= 4:
                    return date_val[:4]
            except:
                pass
        return str(date_val)
    
    def convert_to_int(self, date_val) -> int:
        """Convert date to integer year for comparison"""
        try:
            if date_val is None:
                return 0
            if isinstance(date_val, datetime.datetime):
                return date_val.year
            if isinstance(date_val, int):
                return date_val
            if isinstance(date_val, str):
                # Try to extract year
                if len(date_val) >= 4:
                    return int(date_val[:4])
            return 0
        except:
            return 0
    
    def get_spaces(self, schedule_item: Dict) -> str:
        """
        Get label with indentation and formatting.
        Format: "LayerName - Name (arrow)     " (with spaces based on RelationId)
        """
        layer_name = schedule_item.get('SourceLayer', '')
        name = schedule_item.get('Name', '')
        
        # Combine layername and name
        tree_label = f"{layer_name} - {name}"
        
        # Truncate to 30 characters if too long
        if len(tree_label) > 30:
            tree_label = tree_label[:30]
        
        # Add arrow symbol (using ASCII-safe alternative)
        tree_label = tree_label + "  -> "
        
        # Add spaces based on RelationId (4 spaces per level)
        rel_id = schedule_item.get('RelationId', 0)
        for i in range(rel_id):
            tree_label = tree_label + "    "
        
        return tree_label
    
    def get_labels_without_spaces(self, schedule_item: Dict) -> str:
        """Get label without spaces (just the name)"""
        return schedule_item.get('Name', '')
    
    def check_issues_for_depending(self, schedule_data: List[Dict]) -> bool:
        """
        Check if there are scheduling issues in depending features.
        Iterates backwards and compares child endDate with parent endDate.
        Marks both child and parent if child ends after parent.
        """
        has_issue = False
        
        try:
            # Iterate backwards through schedule data
            for i in range(len(schedule_data) - 1, 0, -1):
                item = schedule_data[i]
                previous_item = schedule_data[i - 1]
                
                # Find parent item (RelationId = item.RelationId - 1)
                is_parent = False
                parent_index = 0
                
                if previous_item.get('RelationId') == item.get('RelationId') - 1:
                    is_parent = True
                    parent_index = i - 1
                
                parent_item = None
                if not is_parent:
                    # Search backwards for parent
                    for j in range(i, -1, -1):
                        if schedule_data[j].get('RelationId') == item.get('RelationId') - 1:
                            parent_item = schedule_data[j]
                            parent_index = j
                            break
                else:
                    parent_item = previous_item
                
                # Compare dates
                if parent_item is not None and item is not None:
                    item_end = self.convert_to_int(item.get('endDate'))
                    parent_end = self.convert_to_int(parent_item.get('endDate'))
                    
                    # If child ends after parent OR child already has issue
                    if item_end > 0 and parent_end > 0:  # Only compare if both have valid dates
                        if item_end > parent_end or item.get('hasIssue', False):
                            schedule_data[i]['hasIssue'] = True
                            schedule_data[parent_index]['hasIssue'] = True
                            has_issue = True
                    elif item.get('hasIssue', False):
                        # Propagate existing issues even without dates
                        schedule_data[i]['hasIssue'] = True
                        schedule_data[parent_index]['hasIssue'] = True
                        has_issue = True
        except Exception as e:
            self.log(f"Error in check_issues_for_depending: {str(e)}", "ERROR")
        
        return has_issue
    
    def check_issues_for_supporting(self, schedule_data: List[Dict]) -> bool:
        """
        Check if there are scheduling issues in supporting features.
        Iterates forward and compares child endDate with parent endDate.
        Marks both parent and child if child ends before parent.
        """
        has_issue = False
        
        try:
            # Iterate forward through schedule data
            for i in range(len(schedule_data) - 1):
                item = schedule_data[i]
                
                if i + 1 < len(schedule_data):
                    next_item = schedule_data[i + 1]
                else:
                    break
                
                # Find child item (RelationId = item.RelationId + 1)
                is_child = False
                child_index = 0
                
                if next_item.get('RelationId') == item.get('RelationId') + 1:
                    is_child = True
                    child_index = i + 1
                
                child_item = None
                if not is_child:
                    # Search forward for child
                    for j in range(i, len(schedule_data)):
                        if schedule_data[j].get('RelationId') == item.get('RelationId') + 1:
                            child_item = schedule_data[j]
                            child_index = j
                            break
                else:
                    child_item = next_item
                
                # Compare dates
                if child_item is not None and item is not None:
                    child_end = self.convert_to_int(child_item.get('endDate'))
                    item_end = self.convert_to_int(item.get('endDate'))
                    
                    # If child ends before parent OR child already has issue
                    if child_end > 0 and item_end > 0:  # Only compare if both have valid dates
                        if child_end < item_end or child_item.get('hasIssue', False):
                            schedule_data[i]['hasIssue'] = True
                            schedule_data[child_index]['hasIssue'] = True
                            has_issue = True
                    elif child_item.get('hasIssue', False):
                        # Propagate existing issues even without dates
                        schedule_data[i]['hasIssue'] = True
                        schedule_data[child_index]['hasIssue'] = True
                        has_issue = True
        except Exception as e:
            self.log(f"Error in check_issues_for_supporting: {str(e)}", "ERROR")
        
        return has_issue
    
    def process_infratagging_summary(self, dependency_type: str) -> List[Dict]:
        """Process infrastructure tagging summary for given type"""
        try:
            self.log(f"Processing {dependency_type} features...")
            arcpy.AddMessage(f"Processing {dependency_type} features...")
            
            self.dependency_all = self.get_dependency_links_all(dependency_type)
            self.log(f"Retrieved {len(self.dependency_all)} dependency links")
            arcpy.AddMessage(f"Retrieved {len(self.dependency_all)} dependency links")
            
            layers = self.get_infra_layers()
            self.log(f"Retrieved {len(layers)} layers")
            arcpy.AddMessage(f"Retrieved {len(layers)} layers")
            
            # Create lookup by BOTH name AND id for better matching
            layer_dict_by_name = {layer.get('LAYER_NAME'): layer for layer in layers if layer.get('LAYER_NAME')}
            # Convert layer IDs to strings for consistent matching
            layer_dict_by_id = {str(layer.get('LAYER_ID')): layer for layer in layers if layer.get('LAYER_ID')}
            
            infra_features = []
            type_id = 0 if dependency_type == "Depending" else 1
            
            # Track unique features
            seen_keys = set()
            
            for dep in self.dependency_all:
                # Get both layer name and ID from dependency
                source_layer = dep.get('SOURCELAYER', '')
                source_layer_id = dep.get('SOURCE_LAYERID')
                source_feature_id = str(dep.get('SOURCE_FEATUREID', ''))
                
                # Create unique key
                key = (source_feature_id, source_layer_id, type_id)
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                
                # Use RECURSIVE filter to build full dependency tree
                schedule_data_list = []
                has_issues_ref = [False]  # Use list to pass by reference
                
                self.filter_schedule_links(
                    source_layer,
                    source_feature_id,
                    dep.get('SOURCE_START_DATE', ''),
                    dep.get('SOURCE_END_DATE', ''),
                    dep.get('SOURCE_DESCRIPTION', ''),
                    schedule_data_list,
                    has_issues_ref,
                    0,  # Initial RelationId
                    dependency_type,
                    self.dependency_all
                )
                
                # Try matching by ID first (more reliable), then by name
                # Convert to string for consistent matching
                matched_layer = layer_dict_by_id.get(str(source_layer_id)) if source_layer_id else None
                if not matched_layer and source_layer:
                    matched_layer = layer_dict_by_name.get(source_layer)
                
                if matched_layer:
                    # Ensure Layer_Id is an integer for consistent matching
                    layer_id_val = matched_layer.get('LAYER_ID')
                    if isinstance(layer_id_val, str):
                        layer_id_val = int(layer_id_val) if layer_id_val.isdigit() else layer_id_val
                    
                    infra_features.append({
                        'Category': 1 if has_issues_ref[0] else 0,
                        'Type': type_id,
                        'FeatureId': source_feature_id,
                        'Layer_Id': layer_id_val,
                        'Layer': matched_layer.get('LAYER_NAME'),
                        'ChartJSON': None,
                        'ChartHeight': 0
                    })
                else:
                    # Use source_layer_id if available
                    infra_features.append({
                        'Category': 1 if has_issues_ref[0] else 0,
                        'Type': type_id,
                        'FeatureId': source_feature_id,
                        'Layer_Id': source_layer_id if source_layer_id else -1,
                        'Layer': source_layer if source_layer else f"Unknown Layer (ID:{source_layer_id})",
                        'ChartJSON': None,
                        'ChartHeight': 0
                    })
            
            self.log(f"Processed {len(infra_features)} unique {dependency_type} features")
            arcpy.AddMessage(f"Processed {len(infra_features)} unique {dependency_type} features")
            return infra_features
            
        except Exception as e:
            self.log(f"Error in process_infratagging_summary: {str(e)}", "ERROR")
            raise
    
    def prepare_chart_json_data(self, island_wide_data: Dict) -> str:
        """
        Prepare Chart.js configuration JSON for visualization.
        Matches .NET PrepareChartJSONData function exactly.
        """
        try:
            schedule_data = island_wide_data.get('ScheduleData', [])
            
            if not schedule_data:
                return "{}"
            
            label_data = []
            labels_without_spaces = []
            background_color = []
            staging_year = []
            check_distinct_values = []
            
            # Check for overall issues
            has_issue = False
            if island_wide_data.get('Type') == "Depending":
                has_issue = self.check_issues_for_depending(schedule_data)
            else:
                has_issue = self.check_issues_for_supporting(schedule_data)
            
            # Process each schedule item
            for item in schedule_data:
                # Check if this combination already exists
                is_duplicate = any(
                    d.get('Id') == item.get('Id') and 
                    d.get('SourceLayer') == item.get('SourceLayer') and 
                    d.get('RelationId') == item.get('RelationId')
                    for d in check_distinct_values
                )
                
                if not is_duplicate:
                    # Add label with indentation
                    tree_label = self.get_spaces(item)
                    label_data.append(tree_label)
                    
                    # Add label without spaces
                    labels_without_spaces.append(self.get_labels_without_spaces(item))
                    
                    # Add year data [startDate, endDate, SourceLayer]
                    lst_yr = [
                        item.get('startDate', ''),
                        item.get('endDate', ''),
                        item.get('SourceLayer', '')
                    ]
                    staging_year.append(lst_yr)
                    
                    # Add background color (red for issues, green for no issues)
                    color = "rgba(255, 0, 0, 0.5)" if item.get('hasIssue', False) else "rgba(0, 128, 0, 0.5)"
                    background_color.append(color)
                    
                    # Track this item as processed
                    check_distinct_values.append({
                        'Id': item.get('Id'),
                        'Name': item.get('Name'),
                        'RelationId': item.get('RelationId'),
                        'SourceLayer': item.get('SourceLayer')
                    })
            
            # If there's an overall issue, mark the first item as red
            if has_issue and len(background_color) > 0:
                background_color[0] = "rgba(255, 0, 0, 0.5)"
            
            # Build Chart.js configuration JSON string
            chart_json = {
                "type": "horizontalBar",
                "responsive": True,
                "data": {
                    "labels": label_data,
                    "datasets": [{
                        "backgroundColor": background_color,
                        "data": staging_year,
                        "maxBarThickness": 30
                    }]
                },
                "options": {
                    "maintainAspectRatio": False,
                    "responsive": False,
                    "title": {
                        "display": True,
                        "text": "Infra Schedules by Year"
                    },
                    "legend": {
                        "display": False
                    },
                    "events": ["click", "mousemove"],
                    "tooltips": {
                        "callbacks": {}
                    },
                    "scales": {
                        "xAxes": [{
                            "ticks": {
                                "stepSize": 1,
                                "min": 2010,
                                "max": 2040
                            }
                        }],
                        "yAxes": [{
                            "ticks": {
                                "fontSize": 14
                            }
                        }]
                    },
                    "plugins": {
                        "datalabels": {
                            "align": "end",
                            "anchor": "start",
                            "font": {
                                "size": 12,
                                "weight": 400
                            },
                            "color": "white",
                            "formatter": "function(value){return value[2]}"
                        }
                    }
                }
            }
            
            return json.dumps(chart_json)
            
        except Exception as e:
            self.log(f"Error in prepare_chart_json_data: {str(e)}", "ERROR")
            return "{}"
    
    def get_chart_height(self, schedule_count: int) -> int:
        """Calculate chart height based on number of schedule items"""
        base_height = 100
        item_height = 30
        return base_height + (schedule_count * item_height)
    
    def get_schedule_data_island_wide(self, mapping_list: List[Dict], 
                                      dependency_type: str) -> List[Dict]:
        """
        Get schedule data for island-wide processing.
        Matches .NET GetScheduleDatasIslandWide function.
        """
        try:
            dependency_raw_all = self.get_dependency_links_all(dependency_type)
            island_wide_data = []
            
            for item in mapping_list:
                layer = item['Layer']
                feature_id = str(item['FeatureId'])
                item_type = 0 if item['Type'] == 0 else 1
                
                # Build schedule data using RECURSIVE filter
                schedule_data_list = []
                has_issues_ref = [False]
                
                # ALWAYS call filter_schedule_links (like .NET does)
                # Pass empty strings for initial dates/description (will be populated from dependencies)
                self.filter_schedule_links(
                    layer,
                    feature_id,
                    "",  # startDate - empty initially
                    "",  # endDate - empty initially
                    "",  # description - empty initially
                    schedule_data_list,
                    has_issues_ref,
                    0,   # relId starts at 0
                    "Depending" if item_type == 0 else "Supporting",
                    dependency_raw_all
                )
                
                # Special case: if only 1 schedule item, check if this is actually a destination
                if len(schedule_data_list) == 1:
                    filtered_as_dest = [
                        d for d in dependency_raw_all 
                        if d.get('DESTINATIONLAYER') == layer and 
                        str(d.get('DESTINATION_FEATUREID')) == str(feature_id)
                    ]
                    
                    if len(filtered_as_dest) > 0:
                        schedule_data_list = []
                        schedule_data_list.append({
                            'Name': filtered_as_dest[0].get('DESTINATION_DESCRIPTION', ''),
                            'SourceLayer': filtered_as_dest[0].get('DESTINATIONLAYER', ''),
                            'Id': str(filtered_as_dest[0].get('DESTINATION_FEATUREID', '')),
                            'startDate': self.format_date(filtered_as_dest[0].get('DESTINATION_START_DATE')),
                            'endDate': self.format_date(filtered_as_dest[0].get('DESTINATION_END_DATE')),
                            'RelationId': 1,
                            'hasIssue': False
                        })
                
                # Create island-wide data item
                # Ensure LayerId is an integer for consistent matching
                layer_id_for_chart = item['Layer_Id']
                if isinstance(layer_id_for_chart, str) and layer_id_for_chart.isdigit():
                    layer_id_for_chart = int(layer_id_for_chart)
                elif isinstance(layer_id_for_chart, str):
                    # Try to convert, default to -1 if not possible
                    try:
                        layer_id_for_chart = int(layer_id_for_chart)
                    except:
                        layer_id_for_chart = -1
                
                data_item = {
                    'Id': feature_id,
                    'ScheduleData': schedule_data_list,
                    'LayerId': layer_id_for_chart,
                    'Name': layer,
                    'Type': "Depending" if item_type == 0 else "Supporting"
                }
                
                island_wide_data.append(data_item)
            
            # First, run issue detection to update hasIssue flags in schedule data
            issue_count = 0
            for item in island_wide_data:
                if len(item['ScheduleData']) > 0:
                    if item['Type'] == "Depending":
                        has_issue = self.check_issues_for_depending(item['ScheduleData'])
                    else:
                        has_issue = self.check_issues_for_supporting(item['ScheduleData'])
                    
                    if has_issue:
                        issue_count += 1
            
            self.log(f"Issue detection: {issue_count}/{len(island_wide_data)} features have scheduling issues")
            
            # Then generate ChartJSON and ChartHeight (uses updated hasIssue flags)
            for item in island_wide_data:
                item['ChartJSON'] = self.prepare_chart_json_data(item)
                item['ChartHeight'] = self.get_chart_height(len(item['ScheduleData']))
            
            # Log statistics
            empty_count = sum(1 for item in island_wide_data if len(item['ScheduleData']) == 0)
            if empty_count > 0:
                self.log(f"{empty_count}/{len(island_wide_data)} features have NO schedule data", "WARNING")
            
            avg_schedule_count = sum(len(item['ScheduleData']) for item in island_wide_data) / len(island_wide_data) if island_wide_data else 0
            self.log(f"Average schedule items per feature: {avg_schedule_count:.2f}")
            
            return island_wide_data
            
        except Exception as e:
            self.log(f"Error in get_schedule_data_island_wide: {str(e)}", "ERROR")
            raise
    
    def add_to_summary_cache_results(self, lst_depending: List[Dict], 
                                    lst_supporting: List[Dict]):
        """Add processed results to summary cache table"""
        try:
            self.log("Generating chart data for Depending features...")
            depending_charts = self.get_schedule_data_island_wide(lst_depending, "Depending")
            
            self.log("Generating chart data for Supporting features...")
            supporting_charts = self.get_schedule_data_island_wide(lst_supporting, "Supporting")
            
            # Update Depending features with chart data AND issue status
            depending_matched = 0
            depending_issues = 0
            
            for feature in lst_depending:
                # Robust matching - handle both int and string comparisons
                feature_layer_id = feature['Layer_Id']
                matching_charts = [c for c in depending_charts 
                                 if str(c['Id']) == str(feature['FeatureId']) and 
                                 (c['LayerId'] == feature_layer_id or 
                                  str(c['LayerId']) == str(feature_layer_id))]
                
                if matching_charts:
                    chart_data = matching_charts[0]
                    feature['ChartJSON'] = chart_data['ChartJSON']
                    feature['ChartHeight'] = chart_data['ChartHeight']
                    
                    # Update Category based on detected issues in schedule data
                    has_issue = any(item.get('hasIssue', False) for item in chart_data.get('ScheduleData', []))
                    if has_issue:
                        feature['Category'] = 1  # Has issues
                        depending_issues += 1
                    
                    depending_matched += 1
            
            self.log(f"Matched chart data for {depending_matched}/{len(lst_depending)} Depending features")
            self.log(f"Depending: {depending_issues} features WITH issues, {depending_matched - depending_issues} WITHOUT issues")
            
            # Update Supporting features with chart data AND issue status
            supporting_matched = 0
            supporting_issues = 0
            for feature in lst_supporting:
                # Robust matching - handle both int and string comparisons
                feature_layer_id = feature['Layer_Id']
                matching_charts = [c for c in supporting_charts 
                                 if str(c['Id']) == str(feature['FeatureId']) and 
                                 (c['LayerId'] == feature_layer_id or 
                                  str(c['LayerId']) == str(feature_layer_id))]
                
                if matching_charts:
                    chart_data = matching_charts[0]
                    feature['ChartJSON'] = chart_data['ChartJSON']
                    feature['ChartHeight'] = chart_data['ChartHeight']
                    
                    # Update Category based on detected issues in schedule data
                    has_issue = any(item.get('hasIssue', False) for item in chart_data.get('ScheduleData', []))
                    if has_issue:
                        feature['Category'] = 1  # Has issues
                        supporting_issues += 1
                    
                    supporting_matched += 1
            
            self.log(f"Matched chart data for {supporting_matched}/{len(lst_supporting)} Supporting features")
            self.log(f"Supporting: {supporting_issues} features WITH issues, {supporting_matched - supporting_issues} WITHOUT issues")
            
            self.save_to_cache_table(lst_depending, lst_supporting)
            
        except Exception as e:
            self.log(f"Error in add_to_summary_cache_results: {str(e)}", "ERROR")
            raise
    
    def save_to_cache_table(self, lst_depending: List[Dict], lst_supporting: List[Dict]):
        """Save results directly to cache table - OBJECTID is auto-generated by ArcGIS"""
        try:
            cache_table = self.app_schema.rstrip('.') + ".INFRATAGGING_SUMMARY_CACHE"
            cache_table_path = os.path.join(self.sde_path, cache_table)
            
            # Step 1: Clear cache table using Truncate (faster than DELETE)
            self.log("Clearing cache table...")
            try:
                arcpy.TruncateTable_management(cache_table_path)
                self.log("Cache table cleared using TRUNCATE")
            except:
                # Fallback to DELETE if TRUNCATE fails
                clear_sql = f"DELETE FROM {cache_table}"
                self.execute_sql_direct(clear_sql)
                self.log("Cache table cleared using DELETE")
            
            # Step 2: Insert using InsertCursor (OBJECTID auto-generated)
            all_features = lst_depending + lst_supporting
            total_to_insert = len(all_features)
            
            # Log how many records will be inserted
            self.log("="*80)
            self.log(f"INSERTING RECORDS TO CACHE TABLE:")
            arcpy.AddMessage("="*80)
            arcpy.AddMessage(f"INSERTING RECORDS TO CACHE TABLE:")
            
            self.log(f"  - Depending Features: {len(lst_depending)}")
            arcpy.AddMessage(f"  - Depending Features: {len(lst_depending)}")
            
            self.log(f"  - Supporting Features: {len(lst_supporting)}")
            arcpy.AddMessage(f"  - Supporting Features: {len(lst_supporting)}")
            
            self.log(f"  - Total Records to Insert: {total_to_insert}")
            arcpy.AddMessage(f"  - Total Records to Insert: {total_to_insert}")
            
            self.log("="*80)
            arcpy.AddMessage("="*80)
            
            total_inserted = 0
            
            # Define fields to insert (NO OBJECTID - it's auto-generated!)
            insert_fields = ['LAYER_ID', 'FEATURE_ID', 'CATEGORY', 'UPDATEDDATE', 'TYPE', 'CHARTJSON', 'CHARTHEIGHT']
            
            with arcpy.da.InsertCursor(cache_table_path, insert_fields) as cursor:
                for feature in all_features:
                    feature_id = str(feature['FeatureId'])
                    chart_json = feature.get('ChartJSON', '') or ''
                    
                    row = [
                        feature['Layer_Id'],           # LAYER_ID
                        feature_id,                    # FEATURE_ID
                        feature['Category'],           # CATEGORY
                        datetime.datetime.now(),       # UPDATEDDATE
                        feature['Type'],               # TYPE
                        chart_json,                    # CHARTJSON
                        feature.get('ChartHeight', 0)  # CHARTHEIGHT
                    ]
                    
                    cursor.insertRow(row)
                    total_inserted += 1
                    
                    if total_inserted % 100 == 0:
                        progress_msg = f"Progress: {total_inserted}/{total_to_insert} records inserted ({int(total_inserted/total_to_insert*100)}%)"
                        self.log(progress_msg)
                        arcpy.AddMessage(progress_msg)
            
            # Final summary
            self.log("="*80)
            arcpy.AddMessage("="*80)
            
            self.log(f"[SUCCESS] INSERTION COMPLETED SUCCESSFULLY")
            arcpy.AddMessage(f"[SUCCESS] INSERTION COMPLETED SUCCESSFULLY")
            
            self.log(f"  - Total Records Inserted: {total_inserted}")
            arcpy.AddMessage(f"  - Total Records Inserted: {total_inserted}")
            
            self.log(f"  - Depending Features: {len(lst_depending)}")
            arcpy.AddMessage(f"  - Depending Features: {len(lst_depending)}")
            
            self.log(f"  - Supporting Features: {len(lst_supporting)}")
            arcpy.AddMessage(f"  - Supporting Features: {len(lst_supporting)}")
            
            self.log("="*80)
            arcpy.AddMessage("="*80)
            
        except Exception as e:
            self.log(f"Error in save_to_cache_table: {str(e)}", "ERROR")
            self.log(f"Full error: {traceback.format_exc()}", "ERROR")
            raise
    
    def execute(self) -> str:
        """Main execution method"""
        status = "Failed"
        
        try:
            # Setup ArcGIS progressor
            arcpy.SetProgressor("default", "Starting Infratagging Summary Generation...")
            
            self.log("="*80)
            arcpy.AddMessage("="*80)
            
            self.log("Started Infratagging Summary Generation Job")
            arcpy.AddMessage("Started Infratagging Summary Generation Job")
            
            self.log("="*80)
            arcpy.AddMessage("="*80)
            
            # Step 1: Process Depending Features
            arcpy.SetProgressorLabel("Processing Depending Features...")
            self.log("Executing for Depending Features")
            arcpy.AddMessage("Executing for Depending Features")
            
            lst_depending = self.process_infratagging_summary("Depending")
            
            self.log(f"Depending Features execution completed. Total Count: {len(lst_depending)}")
            arcpy.AddMessage(f"Depending Features execution completed. Total Count: {len(lst_depending)}")
            
            # Step 2: Process Supporting Features
            arcpy.SetProgressorLabel("Processing Supporting Features...")
            self.log("Executing for Supporting Features")
            arcpy.AddMessage("Executing for Supporting Features")
            
            lst_supporting = self.process_infratagging_summary("Supporting")
            
            self.log(f"Supporting Features execution completed. Total Count: {len(lst_supporting)}")
            arcpy.AddMessage(f"Supporting Features execution completed. Total Count: {len(lst_supporting)}")
            
            # Step 3: Update Cache
            arcpy.SetProgressorLabel("Updating Infratagging Cache table...")
            self.log("Updating Infratagging Cache table")
            arcpy.AddMessage("Updating Infratagging Cache table")
            
            self.add_to_summary_cache_results(lst_depending, lst_supporting)
            
            self.log("Update successful to Infratagging Cache table")
            arcpy.AddMessage("Update successful to Infratagging Cache table")
            
            status = "Success"
            arcpy.ResetProgressor()
            
            # Final summary
            total_records = len(lst_depending) + len(lst_supporting)
            
            # Create summary message for ArcGIS Server (ASCII-safe)
            summary_msg = f"""
{'='*80}
[SUCCESS] JOB COMPLETED SUCCESSFULLY!
{'='*80}
FINAL SUMMARY:
  - Depending Features Processed: {len(lst_depending)}
  - Supporting Features Processed: {len(lst_supporting)}
  - Total Records Inserted to Cache Table: {total_records}
{'='*80}
Log File: {getattr(self, 'log_file_path', 'N/A')}
{'='*80}
"""
            
            # Log to all outputs
            self.log("="*80)
            self.log("[SUCCESS] JOB COMPLETED SUCCESSFULLY!")
            self.log("="*80)
            self.log(f"FINAL SUMMARY:")
            self.log(f"  - Depending Features Processed: {len(lst_depending)}")
            self.log(f"  - Supporting Features Processed: {len(lst_supporting)}")
            self.log(f"  - Total Records Inserted to Cache Table: {total_records}")
            self.log("="*80)
            self.log(f"Log File: {getattr(self, 'log_file_path', 'N/A')}")
            self.log("="*80)
            
            # Add complete summary as single message for ArcGIS Server
            arcpy.AddMessage(summary_msg)
            
            # Also add individual lines
            arcpy.AddMessage("="*80)
            arcpy.AddMessage("[SUCCESS] JOB COMPLETED SUCCESSFULLY!")
            arcpy.AddMessage("="*80)
            arcpy.AddMessage(f"FINAL SUMMARY:")
            arcpy.AddMessage(f"  - Depending Features Processed: {len(lst_depending)}")
            arcpy.AddMessage(f"  - Supporting Features Processed: {len(lst_supporting)}")
            arcpy.AddMessage(f"  - Total Records Inserted to Cache Table: {total_records}")
            arcpy.AddMessage("="*80)
            
            # Set output parameter if exists (for GP tools)
            try:
                if arcpy.Exists("Output_Message"):
                    arcpy.SetParameterAsText(0, summary_msg)
            except:
                pass
            
            # Print summary to console
            print("\n" + "="*80)
            print("FINAL SUMMARY")
            print("="*80)
            print(f"Depending Features: {len(lst_depending)}")
            print(f"Supporting Features: {len(lst_supporting)}")
            print(f"Total Records Inserted: {total_records}")
            print("="*80)
            
            # Write summary to a separate file for easy retrieval by Jenkins
            try:
                summary_file = os.path.join(LOG_FOLDER, time.strftime("%Y%m%d") + "_Summary.txt")
                with open(summary_file, 'w', encoding='utf-8') as f:
                    f.write("="*80 + "\n")
                    f.write("[SUCCESS] JOB COMPLETED SUCCESSFULLY!\n")
                    f.write("="*80 + "\n")
                    f.write(f"Execution Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("-"*80 + "\n")
                    f.write("SUMMARY:\n")
                    f.write(f"  - Depending Features Processed: {len(lst_depending)}\n")
                    f.write(f"  - Supporting Features Processed: {len(lst_supporting)}\n")
                    f.write(f"  - Total Records Inserted: {total_records}\n")
                    f.write("="*80 + "\n")
                    f.write(f"Log File: {getattr(self, 'log_file_path', 'N/A')}\n")
                    f.write("="*80 + "\n")
                self.log(f"Summary file: {summary_file}")
                arcpy.AddMessage(f"Summary file: {summary_file}")
            except Exception as summary_error:
                arcpy.AddWarning(f"Could not write summary file: {str(summary_error)}")
            
        except Exception as e:
            arcpy.ResetProgressor()
            self.log(f"ERROR: {str(e)}", "ERROR")
            self.log(traceback.format_exc(), "ERROR")
            status = "Failed"
            
            # Write error summary file
            try:
                summary_file = os.path.join(LOG_FOLDER, time.strftime("%Y%m%d") + "_Summary.txt")
                with open(summary_file, 'w', encoding='utf-8') as f:
                    f.write("="*80 + "\n")
                    f.write("[FAILED] JOB FAILED!\n")
                    f.write("="*80 + "\n")
                    f.write(f"Execution Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Error: {str(e)}\n")
                    f.write("-"*80 + "\n")
                    f.write("Traceback:\n")
                    f.write(traceback.format_exc() + "\n")
                    f.write("="*80 + "\n")
                    f.write(f"Log File: {getattr(self, 'log_file_path', 'N/A')}\n")
                    f.write("="*80 + "\n")
            except:
                pass  # Ignore if summary file write fails
        
        return status

# ========================================================================
# MAIN EXECUTION
# ========================================================================
def main():
    """Main function"""
    try:
        # Print startup info with immediate flush
        print("="*80)
        print("Infrastructure Tagging Summary Generation")
        print("="*80)
        print(f"SDE Path: {SDE_PATH}")
        print(f"Schema: {APP_SCHEMA}")
        print(f"Log Folder: {LOG_FOLDER}")
        print("="*80)
        print()
        sys.stdout.flush()  # Flush immediately
        
        # Add to ArcGIS messages
        arcpy.AddMessage("="*80)
        arcpy.AddMessage("Infrastructure Tagging Summary Generation")
        arcpy.AddMessage("="*80)
        arcpy.AddMessage(f"SDE Path: {SDE_PATH}")
        arcpy.AddMessage(f"Schema: {APP_SCHEMA}")
        arcpy.AddMessage(f"Log Folder: {LOG_FOLDER}")
        arcpy.AddMessage("="*80)
        
        processor = InfraTaggingProcessor()
        status = processor.execute()
        
        print()
        print("="*80)
        if status == "Success":
            print("[SUCCESS] Job completed successfully!")
            print("="*80)
            return 0
        else:
            print("[FAILED] Job failed. Check logs for details.")
            print("="*80)
            return 1
            
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        arcpy.AddError(f"Fatal error: {str(e)}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
