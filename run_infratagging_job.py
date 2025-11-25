"""
Standalone Runner for Infrastructure Tagging Summary Generation

This script can be run directly without ArcGIS Pro/Server for testing
or scheduled execution outside of the GP framework.

Usage:
    python run_infratagging_job.py --config config.json
    
    OR with command-line arguments:
    
    python run_infratagging_job.py \
        --connection "Driver={ODBC Driver 17 for SQL Server};Server=SERVER;Database=DB;Trusted_Connection=yes;" \
        --schema "dbo" \
        --smtp-server "smtp.gmail.com" \
        --smtp-port 587 \
        --from-email "noreply@company.com" \
        --to-emails "admin@company.com,team@company.com"
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
        description='Run Infrastructure Tagging Summary Generation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Using config file
    python run_infratagging_job.py --config config.json
    
    # Using command-line arguments
    python run_infratagging_job.py \\
        --connection "Driver={ODBC Driver 17 for SQL Server};Server=SERVER;Database=DB;Trusted_Connection=yes;" \\
        --schema "dbo"
        """
    )
    
    # Configuration file option
    parser.add_argument('--config', help='Path to JSON configuration file')
    
    # Direct parameter options
    parser.add_argument('--connection', help='SQL Server connection string')
    parser.add_argument('--schema', default='dbo', help='Database schema name')
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
            
        connection_string = config.get('database', {}).get('connection_string')
        app_schema = config.get('database', {}).get('app_schema', 'dbo')
        
        email_config = config.get('email', {})
        smtp_server = email_config.get('smtp_server')
        smtp_port = email_config.get('smtp_port', 587)
        from_email = email_config.get('from_email')
        to_emails = email_config.get('to_emails', [])
        email_username = email_config.get('username')
        email_password = email_config.get('password')
        
    else:
        # Use command-line arguments
        connection_string = args.connection
        app_schema = args.schema
        smtp_server = args.smtp_server
        smtp_port = args.smtp_port
        from_email = args.from_email
        to_emails = args.to_emails.split(',') if args.to_emails else []
        email_username = args.email_username
        email_password = args.email_password
    
    # Validate required parameters
    if not connection_string:
        print("Error: Connection string is required")
        print("Use --connection or provide --config file")
        return 1
        
    if not app_schema:
        print("Error: Schema name is required")
        return 1
    
    print("="*80)
    print("Infrastructure Tagging Summary Generation - Standalone Runner")
    print("="*80)
    print(f"Schema: {app_schema}")
    print(f"Email notifications: {'Enabled' if smtp_server else 'Disabled'}")
    print("="*80)
    print()
    
    try:
        # Import the processor
        from generate_infratagging_summary import InfraTaggingProcessor
        
        # Build email configuration
        email_cfg = None
        if smtp_server and from_email and to_emails:
            email_cfg = {
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
        processor = InfraTaggingProcessor(connection_string, app_schema, email_cfg)
        
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
        print("Make sure you have installed the required dependencies:")
        print("  pip install -r requirements.txt")
        return 1
        
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
