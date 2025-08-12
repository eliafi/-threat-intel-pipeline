#!/usr/bin/env python3

import os
import sys
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from airflow.models import Connection
from airflow import settings

def check_environment_credentials():
    """Check if AWS credentials are available via environment variables"""
    print("🔍 Checking environment variables...")
    
    access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    region = os.environ.get('AWS_DEFAULT_REGION')
    
    print(f"   AWS_ACCESS_KEY_ID: {'✅ Set' if access_key else '❌ Not set'}")
    print(f"   AWS_SECRET_ACCESS_KEY: {'✅ Set' if secret_key else '❌ Not set'}")
    print(f"   AWS_DEFAULT_REGION: {region if region else '❌ Not set'}")
    
    return bool(access_key and secret_key)

def check_airflow_connection():
    """Check if Airflow AWS connection exists"""
    print("\n🔍 Checking Airflow connections...")
    
    try:
        session = settings.Session()
        connection = session.query(Connection).filter(Connection.conn_id == 'aws_default').first()
        
        if connection:
            print("   ✅ aws_default connection found")
            print(f"   Connection Type: {connection.conn_type}")
            print(f"   Login (Access Key): {'✅ Set' if connection.login else '❌ Not set'}")
            print(f"   Password (Secret Key): {'✅ Set' if connection.password else '❌ Not set'}")
            return True
        else:
            print("   ❌ aws_default connection not found")
            return False
            
    except Exception as e:
        print(f"   ❌ Error checking connections: {e}")
        return False

def test_boto3_credentials():
    """Test if boto3 can use the credentials"""
    print("\n🔍 Testing boto3 AWS access...")
    
    try:
        s3 = boto3.client('s3')
        print("   ✅ boto3 client created successfully")
        
        # Try to list buckets
        buckets = s3.list_buckets()
        print(f"   ✅ Successfully connected to AWS! Found {len(buckets['Buckets'])} buckets")
        
        # List bucket names
        if buckets['Buckets']:
            print("   📋 Your S3 buckets:")
            for bucket in buckets['Buckets']:
                print(f"      - {bucket['Name']}")
        else:
            print("   📋 No S3 buckets found in your account")
            
        return True
        
    except NoCredentialsError:
        print("   ❌ No AWS credentials found")
        return False
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDenied':
            print("   ❌ Access denied - check IAM permissions")
        else:
            print(f"   ❌ AWS error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def test_s3_bucket_access(bucket_name="threat-intel-data-lake"):
    """Test access to specific bucket"""
    print(f"\n🪣 Testing access to bucket: {bucket_name}")
    
    try:
        s3 = boto3.client('s3')
        
        # Check if bucket exists
        try:
            s3.head_bucket(Bucket=bucket_name)
            print(f"   ✅ Bucket '{bucket_name}' exists and is accessible!")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"   📝 Bucket '{bucket_name}' doesn't exist (will be created automatically)")
                return True
            elif error_code == '403':
                print(f"   ❌ Access denied to bucket '{bucket_name}' - check IAM permissions")
                return False
            else:
                print(f"   ❌ Error accessing bucket: {e}")
                return False
                
    except Exception as e:
        print(f"   ❌ Error testing bucket access: {e}")
        return False

def main():
    """Run comprehensive AWS integration test"""
    print("🧪 Comprehensive AWS Integration Test")
    print("=" * 50)
    
    # Test 1: Environment credentials
    env_creds = check_environment_credentials()
    
    # Test 2: Airflow connection
    airflow_conn = check_airflow_connection()
    
    # Test 3: boto3 access
    boto3_access = test_boto3_credentials()
    
    # Test 4: Bucket access (only if boto3 works)
    bucket_access = False
    if boto3_access:
        bucket_access = test_s3_bucket_access()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"   Environment Variables: {'✅' if env_creds else '❌'}")
    print(f"   Airflow Connection:    {'✅' if airflow_conn else '❌'}")
    print(f"   AWS Access:            {'✅' if boto3_access else '❌'}")
    print(f"   Bucket Access:         {'✅' if bucket_access else '❌'}")
    
    if boto3_access and bucket_access:
        print("\n🎉 All tests passed! Your AWS integration is ready!")
        print("🚀 You can now run your threat intelligence DAG with S3 upload")
    else:
        print("\n⚠️  Some tests failed. Next steps:")
        if not airflow_conn:
            print("   1. Set up AWS connection in Airflow UI (Admin → Connections)")
        if not boto3_access:
            print("   2. Verify your AWS Access Key ID and Secret Access Key")
            print("   3. Check IAM user permissions")
        print("   4. See docs/S3_SETUP.md for detailed instructions")

if __name__ == "__main__":
    main()
