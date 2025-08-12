#!/usr/bin/env python3
"""
Comprehensive diagnostic script for AWS connection issues
"""
import os
import sys

def check_environment_variables():
    """Check for AWS environment variables"""
    print("🔍 Checking Environment Variables...")
    
    aws_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_DEFAULT_REGION',
        'AWS_SESSION_TOKEN'
    ]
    
    found_vars = {}
    for var in aws_vars:
        value = os.environ.get(var)
        if value:
            found_vars[var] = value[:8] + "..." if len(value) > 8 else value
        else:
            found_vars[var] = "Not set"
    
    for var, value in found_vars.items():
        status = "✅" if value != "Not set" else "❌"
        print(f"  {status} {var}: {value}")
    
    return any(v != "Not set" for v in found_vars.values())

def check_airflow_connection():
    """Check Airflow AWS connection"""
    print("\n🔍 Checking Airflow Connection...")
    
    try:
        from airflow.hooks.base import BaseHook
        
        # Try to get the connection
        try:
            conn = BaseHook.get_connection('aws_default')
            print("✅ Airflow connection 'aws_default' found!")
            print(f"  - Connection type: {conn.conn_type}")
            print(f"  - Host: {conn.host}")
            print(f"  - Login: {conn.login[:8] + '...' if conn.login and len(conn.login) > 8 else conn.login}")
            print(f"  - Password: {'Set' if conn.password else 'Not set'}")
            print(f"  - Extra: {conn.extra}")
            
            return True
            
        except Exception as e:
            print(f"❌ Could not retrieve aws_default connection: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ Could not import Airflow BaseHook: {e}")
        return False

def check_boto3_availability():
    """Check if boto3 is available and can be imported"""
    print("\n🔍 Checking boto3 availability...")
    
    try:
        import boto3
        print("✅ boto3 successfully imported!")
        print(f"  - boto3 version: {boto3.__version__}")
        
        # Check available credential sources
        session = boto3.Session()
        credentials = session.get_credentials()
        
        if credentials:
            print("✅ boto3 found credentials!")
            print(f"  - Access Key: {credentials.access_key[:8]}...")
            print(f"  - Method: {credentials.method if hasattr(credentials, 'method') else 'Unknown'}")
        else:
            print("❌ boto3 could not find credentials")
            
        return credentials is not None
        
    except ImportError as e:
        print(f"❌ Could not import boto3: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking boto3: {e}")
        return False

def check_aws_cli_config():
    """Check for AWS CLI configuration files"""
    print("\n🔍 Checking AWS CLI configuration...")
    
    home_dir = os.path.expanduser("~")
    aws_dir = os.path.join(home_dir, ".aws")
    
    config_file = os.path.join(aws_dir, "config")
    credentials_file = os.path.join(aws_dir, "credentials")
    
    if os.path.exists(aws_dir):
        print(f"✅ AWS directory found: {aws_dir}")
        
        if os.path.exists(config_file):
            print(f"✅ AWS config file found: {config_file}")
        else:
            print(f"❌ AWS config file not found: {config_file}")
            
        if os.path.exists(credentials_file):
            print(f"✅ AWS credentials file found: {credentials_file}")
        else:
            print(f"❌ AWS credentials file not found: {credentials_file}")
    else:
        print(f"❌ AWS directory not found: {aws_dir}")

def test_s3_direct():
    """Test S3 connection directly"""
    print("\n🔍 Testing direct S3 connection...")
    
    try:
        import boto3
        from botocore.exceptions import NoCredentialsError, ClientError
        
        # Try different ways to create S3 client
        methods = [
            ("Default session", lambda: boto3.client('s3')),
            ("With eu-north-1 region", lambda: boto3.client('s3', region_name='eu-north-1')),
        ]
        
        for method_name, create_client in methods:
            try:
                print(f"  Testing {method_name}...")
                s3_client = create_client()
                response = s3_client.list_buckets()
                print(f"    ✅ Success! Found {len(response.get('Buckets', []))} buckets")
                
                # List bucket names
                for bucket in response.get('Buckets', [])[:3]:  # Show first 3
                    print(f"      - {bucket['Name']}")
                    
                return True
                
            except NoCredentialsError:
                print(f"    ❌ No credentials for {method_name}")
            except ClientError as e:
                print(f"    ❌ Client error for {method_name}: {e.response['Error']['Code']}")
            except Exception as e:
                print(f"    ❌ Error for {method_name}: {e}")
        
        return False
        
    except ImportError:
        print("  ❌ boto3 not available")
        return False

def suggest_solutions():
    """Suggest solutions based on findings"""
    print("\n" + "="*60)
    print("💡 SUGGESTED SOLUTIONS")
    print("="*60)
    
    print("""
1. **If Airflow connection is not working:**
   - Open Airflow UI: http://localhost:8080
   - Go to Admin → Connections
   - Find or create 'aws_default' connection
   - Set:
     * Connection Type: Amazon Web Services
     * AWS Access Key ID: (your IAM user access key)
     * AWS Secret Access Key: (your IAM user secret key)
     * Region Name: eu-north-1

2. **If environment variables are not set:**
   - Add to your docker-compose.yaml:
     ```yaml
     environment:
       - AWS_ACCESS_KEY_ID=your_access_key
       - AWS_SECRET_ACCESS_KEY=your_secret_key
       - AWS_DEFAULT_REGION=eu-north-1
     ```

3. **If you need to restart services:**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

4. **Test after configuration:**
   ```bash
   docker-compose exec airflow-worker python /opt/airflow/dags/test_eu_north_connection.py
   ```
""")

def main():
    """Run all diagnostic checks"""
    print("🔧 AWS Connection Diagnostic Tool")
    print("="*60)
    
    # Run all checks
    env_ok = check_environment_variables()
    airflow_ok = check_airflow_connection()
    boto3_ok = check_boto3_availability()
    check_aws_cli_config()
    s3_ok = test_s3_direct()
    
    # Summary
    print("\n" + "="*60)
    print("📊 DIAGNOSTIC SUMMARY")
    print("="*60)
    
    checks = [
        ("Environment Variables", env_ok),
        ("Airflow Connection", airflow_ok),
        ("boto3 Credentials", boto3_ok),
        ("S3 Direct Access", s3_ok)
    ]
    
    for check_name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {check_name}")
    
    if not any(result for _, result in checks):
        print("\n⚠️  No AWS credentials found anywhere!")
        print("   You need to configure AWS credentials.")
    elif any(result for _, result in checks):
        print(f"\n✅ Found working credentials!")
    
    suggest_solutions()

if __name__ == "__main__":
    main()
