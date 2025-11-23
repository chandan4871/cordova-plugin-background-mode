"""
Test and Validation Script for Infrastructure Tagging GP Tool

This script validates that all prerequisites are met before deploying
the GP service to ArcGIS Server.

Usage:
    python test_setup.py --connection "YOUR_CONNECTION_STRING" --schema "dbo"
"""

import sys
import argparse


def test_python_version():
    """Test Python version compatibility"""
    print("Testing Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"✓ Python version {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"✗ Python version {version.major}.{version.minor}.{version.micro} is too old (requires 3.7+)")
        return False


def test_dependencies():
    """Test that required Python packages are installed"""
    print("\nTesting Python dependencies...")
    
    required_packages = {
        'pyodbc': 'Database connectivity',
        'json': 'JSON processing',
        'datetime': 'Date/time handling',
        'smtplib': 'Email notifications',
    }
    
    all_ok = True
    for package, description in required_packages.items():
        try:
            __import__(package)
            print(f"✓ {package}: {description}")
        except ImportError:
            print(f"✗ {package}: {description} - NOT INSTALLED")
            all_ok = False
            
    # Test optional arcpy
    try:
        import arcpy
        print(f"✓ arcpy: ArcGIS Python package (version: {arcpy.GetInstallInfo()['Version']})")
    except ImportError:
        print("⚠ arcpy: Not available (only required when running as GP tool)")
        
    return all_ok


def test_database_connection(connection_string):
    """Test database connection"""
    print("\nTesting database connection...")
    
    try:
        import pyodbc
        conn = pyodbc.connect(connection_string, timeout=10)
        print("✓ Successfully connected to database")
        
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        print(f"  SQL Server version: {version.split('-')[0].strip()}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Failed to connect to database")
        print(f"  Error: {str(e)}")
        return False


def test_database_tables(connection_string, schema):
    """Test that required database tables exist"""
    print("\nTesting database tables...")
    
    required_tables = [
        'INFRATAGGING_MAPPING',
        'INFRATAGGING_MAPPING_SUPP_VW',
        'INFRATAGGING_LAYERS_VW',
        'INFRA_CONS_STAGINGYR_VW',
        'INFRATAGGING_SUMMARY_CACHE'
    ]
    
    try:
        import pyodbc
        conn = pyodbc.connect(connection_string, timeout=10)
        cursor = conn.cursor()
        
        all_ok = True
        for table in required_tables:
            try:
                cursor.execute(f"SELECT TOP 1 * FROM {schema}.{table}")
                cursor.fetchone()
                print(f"✓ {schema}.{table}")
            except Exception as e:
                print(f"✗ {schema}.{table} - {str(e)}")
                all_ok = False
                
        cursor.close()
        conn.close()
        return all_ok
        
    except Exception as e:
        print(f"✗ Failed to test tables: {str(e)}")
        return False


def test_database_permissions(connection_string, schema):
    """Test database permissions"""
    print("\nTesting database permissions...")
    
    try:
        import pyodbc
        conn = pyodbc.connect(connection_string, timeout=10)
        cursor = conn.cursor()
        
        # Test SELECT permission
        try:
            cursor.execute(f"SELECT TOP 1 * FROM {schema}.INFRATAGGING_LAYERS_VW")
            cursor.fetchone()
            print("✓ SELECT permission on views")
        except Exception as e:
            print(f"✗ SELECT permission denied: {str(e)}")
            return False
            
        # Test INSERT/DELETE permission on cache table
        try:
            test_id = 'TEST_VALIDATION_12345'
            cursor.execute(f"""
                INSERT INTO {schema}.INFRATAGGING_SUMMARY_CACHE 
                (FEATUREID, LAYER_ID, LAYER_NAME, TYPE, CATEGORY, CREATED_DATE)
                VALUES (?, -999, 'TEST', 0, 0, GETDATE())
            """, test_id)
            conn.commit()
            print("✓ INSERT permission on cache table")
            
            cursor.execute(f"DELETE FROM {schema}.INFRATAGGING_SUMMARY_CACHE WHERE FEATUREID = ?", test_id)
            conn.commit()
            print("✓ DELETE permission on cache table")
            
        except Exception as e:
            print(f"✗ INSERT/DELETE permission denied: {str(e)}")
            return False
            
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Failed to test permissions: {str(e)}")
        return False


def test_email_config(smtp_server, smtp_port, from_email):
    """Test email configuration"""
    print("\nTesting email configuration...")
    
    if not all([smtp_server, smtp_port, from_email]):
        print("⚠ Email configuration not provided (optional)")
        return True
        
    try:
        import smtplib
        import socket
        
        # Test SMTP server connectivity
        print(f"  Testing connection to {smtp_server}:{smtp_port}...")
        
        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.ehlo()
            if server.has_extn('STARTTLS'):
                server.starttls()
                print("✓ SMTP server is reachable and supports TLS")
            else:
                print("✓ SMTP server is reachable (TLS not supported)")
                
        return True
        
    except socket.timeout:
        print(f"✗ Connection to {smtp_server}:{smtp_port} timed out")
        return False
    except Exception as e:
        print(f"✗ Email configuration error: {str(e)}")
        return False


def test_script_files():
    """Test that required script files exist"""
    print("\nTesting script files...")
    
    import os
    
    required_files = [
        'generate_infratagging_summary.py',
        'InfraTaggingTools.pyt'
    ]
    
    all_ok = True
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    for filename in required_files:
        filepath = os.path.join(script_dir, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"✓ {filename} ({size:,} bytes)")
        else:
            print(f"✗ {filename} - NOT FOUND")
            all_ok = False
            
    return all_ok


def run_sample_query(connection_string, schema):
    """Run a sample query to verify data"""
    print("\nRunning sample data query...")
    
    try:
        import pyodbc
        conn = pyodbc.connect(connection_string, timeout=10)
        cursor = conn.cursor()
        
        # Count records in mapping tables
        cursor.execute(f"SELECT COUNT(*) FROM {schema}.INFRATAGGING_MAPPING")
        count_depending = cursor.fetchone()[0]
        print(f"  INFRATAGGING_MAPPING: {count_depending:,} records")
        
        cursor.execute(f"SELECT COUNT(*) FROM {schema}.INFRATAGGING_MAPPING_SUPP_VW")
        count_supporting = cursor.fetchone()[0]
        print(f"  INFRATAGGING_MAPPING_SUPP_VW: {count_supporting:,} records")
        
        cursor.execute(f"SELECT COUNT(*) FROM {schema}.INFRATAGGING_LAYERS_VW")
        count_layers = cursor.fetchone()[0]
        print(f"  INFRATAGGING_LAYERS_VW: {count_layers:,} layers")
        
        if count_depending > 0 and count_supporting > 0 and count_layers > 0:
            print("✓ Sample data exists in all tables")
            return True
        else:
            print("⚠ Some tables are empty")
            return True
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Failed to query sample data: {str(e)}")
        return False


def main():
    """Main test execution"""
    parser = argparse.ArgumentParser(description='Test Infrastructure Tagging GP Tool setup')
    parser.add_argument('--connection', required=True, help='SQL Server connection string')
    parser.add_argument('--schema', default='dbo', help='Database schema name')
    parser.add_argument('--smtp-server', help='SMTP server for email testing (optional)')
    parser.add_argument('--smtp-port', type=int, default=587, help='SMTP port (default: 587)')
    parser.add_argument('--from-email', help='From email address (optional)')
    
    args = parser.parse_args()
    
    print("="*80)
    print("Infrastructure Tagging GP Tool - Setup Validation")
    print("="*80)
    
    results = []
    
    # Run tests
    results.append(("Python Version", test_python_version()))
    results.append(("Python Dependencies", test_dependencies()))
    results.append(("Script Files", test_script_files()))
    results.append(("Database Connection", test_database_connection(args.connection)))
    results.append(("Database Tables", test_database_tables(args.connection, args.schema)))
    results.append(("Database Permissions", test_database_permissions(args.connection, args.schema)))
    results.append(("Sample Data Query", run_sample_query(args.connection, args.schema)))
    
    if args.smtp_server and args.from_email:
        results.append(("Email Configuration", test_email_config(args.smtp_server, args.smtp_port, args.from_email)))
    
    # Summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
        
    print("-"*80)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! You're ready to deploy.")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed. Please fix the issues before deploying.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
