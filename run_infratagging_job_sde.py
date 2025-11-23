"""
Standalone Runner for Infrastructure Tagging Summary Generation (SDE Version)

This script can be run directly using SDE connections for database access.

Usage:
    python run_infratagging_job_sde.py --config config_sde.json
    
    OR with command-line arguments:
    
    python run_infratagging_job_sde.py \
        --sde-path "C:\\temp\\SDE_Conn\\ONETOOLDEV_ONETOOL_ARCGIS_CONN_SQL.sde" \
        --schema "ONETOOLAPP." \
        --log-folder "C:\\temp\\GPLogs"
"""

import sys
import argparse
import json
import os


def load_config(config_file):
    """Load configuration from JSON file"""
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"Error loading config file: {str(e)}")
        return None


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description='Run Infrastructure Tagging Summary Generation (SDE Version)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Using config file
    python run_infratagging_job_sde.py --config config_sde.json
    
    # Using command-line arguments
    python run_infratagging_job_sde.py \\
        --sde-path "C:\\temp\\SDE_Conn\\ONETOOLDEV_ONETOOL_ARCGIS_CONN_SQL.sde" \\
        --schema "ONETOOLAPP."
        """
    )
    
    # Configuration file option
    parser.add_argument('--config', help='Path to JSON configuration file')
    
    # Direct parameter options
    parser.add_argument('--sde-path', help='Path to SDE connection file')
    parser.add_argument('--schema', default='ONETOOLAPP.', help='Database schema name (with trailing dot)')
    parser.add_argument('--log-folder', help='Path to log folder')
    parser.add_argument('--smtp-server', help='SMTP server address')
    parser.add_argument('--smtp-port', type=int, default=587, help='SMTP port (default: 587)')
    parser.add_argument('--from-email', help='From email address')
    parser.add_argument('--to-emails', help='To email addresses (comma-separated)')
    parser.add_argument('--email-username', help='Email authentication username')
    parser.add_argument('--email-password', help='Email authentication password')
    
    args = parser.parse_args()
    
    # Load configuration
    if args.config:
        config = load_config(args.config)
        if not config:
            return 1
            
        sde_path = config.get('database', {}).get('sde_path')
        app_schema = config.get('database', {}).get('app_schema', 'ONETOOLAPP.')
        log_folder = config.get('logging', {}).get('log_folder')
        
        email_config = config.get('email', {})
        smtp_server = email_config.get('smtp_server')
        smtp_port = email_config.get('smtp_port', 587)
        from_email = email_config.get('from_email')
        to_emails = email_config.get('to_emails', [])
        email_username = email_config.get('username')
        email_password = email_config.get('password')
        
    else:
        # Use command-line arguments
        sde_path = args.sde_path
        app_schema = args.schema
        log_folder = args.log_folder
        smtp_server = args.smtp_server
        smtp_port = args.smtp_port
        from_email = args.from_email
        to_emails = args.to_emails.split(',') if args.to_emails else []
        email_username = args.email_username
        email_password = args.email_password
    
    # Validate required parameters
    if not sde_path:
        print("Error: SDE path is required")
        print("Use --sde-path or provide --config file")
        return 1
        
    if not os.path.exists(sde_path):
        print(f"Error: SDE connection file not found: {sde_path}")
        return 1
        
    if not app_schema:
        print("Error: Schema name is required")
        return 1
    
    # Ensure schema has trailing dot
    if not app_schema.endswith('.'):
        app_schema = app_schema + '.'
    
    print("="*80)
    print("Infrastructure Tagging Summary Generation - Standalone Runner (SDE)")
    print("="*80)
    print(f"SDE Path: {sde_path}")
    print(f"Schema: {app_schema}")
    print(f"Log Folder: {log_folder if log_folder else 'Not specified'}")
    print(f"Email notifications: {'Enabled' if smtp_server else 'Disabled'}")
    print("="*80)
    print()
    
    try:
        # Import arcpy
        try:
            import arcpy
        except ImportError:
            print("Error: arcpy module not found")
            print("This script requires ArcGIS Python environment")
            print("Please run from ArcGIS Python Command Prompt or ensure arcpy is available")
            return 1
        
        # Import the processor
        from generate_infratagging_summary_sde import InfraTaggingProcessor
        
        # Build email configuration
        email_cfg = None
        if smtp_server and from_email and to_emails:
            email_cfg = {
                'enabled': True,
                'smtp_server': smtp_server,
                'smtp_port': smtp_port,
                'from_email': from_email,
                'to_emails': to_emails if isinstance(to_emails, list) else [to_emails],
                'username': email_username,
                'password': email_password
            }
            print(f"Email notifications will be sent to: {', '.join(email_cfg['to_emails'])}")
            print()
        
        # Create processor instance
        processor = InfraTaggingProcessor(sde_path, app_schema, log_folder, email_cfg)
        
        # Execute processing
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
            
    except ImportError as e:
        print(f"Error: Could not import required modules")
        print(f"Details: {str(e)}")
        print()
        print("Make sure you are running from ArcGIS Python environment")
        return 1
        
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
