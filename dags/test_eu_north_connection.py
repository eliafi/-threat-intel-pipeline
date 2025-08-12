#!/usr/bin/env python3
"""
Test AWS connection for eu-north-1 region
"""
import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from airflow.hooks.base import BaseHook

def test_aws_credentials():
    """Test AWS credentials access"""
    print("🔍 Testing AWS credentials...")
    
    try:
        # Try to get credentials from environment first
        access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        
        if access_key and secret_key:
            print("✅ Found AWS credentials in environment variables")
            print(f"Access Key ID: {access_key[:8]}...")
        else:
            print("❌ No AWS credentials found in environment")
            
        # Try to get credentials from Airflow connection
        try:
            from airflow.hooks.base import BaseHook
            conn = BaseHook.get_connection('aws_default')
            if conn.login and conn.password:
                print("✅ Found AWS credentials in Airflow connection")
                print(f"Connection ID: aws_default")
                print(f"Login: {conn.login[:8]}...")
            else:
                print("❌ Airflow connection exists but no credentials")
        except Exception as e:
            print(f"❌ Could not get Airflow connection: {e}")
            
    except Exception as e:
        print(f"❌ Error checking credentials: {e}")

def test_s3_connection():
    """Test S3 connection with eu-north-1 region"""
    print("\n🔍 Testing S3 connection...")
    
    try:
        # Create S3 client with eu-north-1 region
        s3_client = boto3.client('s3', region_name='eu-north-1')
        
        # Test by listing buckets
        response = s3_client.list_buckets()
        print("✅ Successfully connected to S3!")
        print(f"Found {len(response.get('Buckets', []))} buckets in your account")
        
        # List bucket names
        for bucket in response.get('Buckets', []):
            print(f"  - {bucket['Name']}")
            
        return True
        
    except NoCredentialsError:
        print("❌ No AWS credentials found")
        return False
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"❌ AWS Client Error: {error_code}")
        print(f"Error message: {e.response['Error']['Message']}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_bucket_access():
    """Test access to threat-intel-pipeline bucket"""
    print("\n🔍 Testing threat-intel-pipeline bucket access...")
    
    try:
        s3_client = boto3.client('s3', region_name='eu-north-1')
        bucket_name = 'threat-intel-pipeline'
        
        # Check if bucket exists and we have access
        try:
            response = s3_client.head_bucket(Bucket=bucket_name)
            print(f"✅ Bucket '{bucket_name}' exists and is accessible!")
            
            # Try to list objects
            response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=5)
            object_count = response.get('KeyCount', 0)
            print(f"✅ Found {object_count} objects in bucket")
            
            if object_count > 0:
                print("Recent objects:")
                for obj in response.get('Contents', []):
                    print(f"  - {obj['Key']} (Size: {obj['Size']} bytes)")
                    
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"❌ Bucket '{bucket_name}' does not exist or is not accessible")
                print("💡 You may need to create the bucket first")
            else:
                print(f"❌ Error accessing bucket: {error_code}")
                print(f"Error message: {e.response['Error']['Message']}")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
        
    return True

def test_s3_upload():
    """Test uploading a small file to S3"""
    print("\n🔍 Testing S3 upload capability...")
    
    try:
        s3_client = boto3.client('s3', region_name='eu-north-1')
        bucket_name = 'threat-intel-pipeline'
        
        # Create a test file content
        test_content = "Test file created by threat-intel-pipeline\nTimestamp: 2025-08-12"
        test_key = "test/connection_test.txt"
        
        # Upload test file
        s3_client.put_object(
            Bucket=bucket_name,
            Key=test_key,
            Body=test_content.encode('utf-8'),
            ContentType='text/plain'
        )
        
        print(f"✅ Successfully uploaded test file to s3://{bucket_name}/{test_key}")
        
        # Verify the upload by reading it back
        response = s3_client.get_object(Bucket=bucket_name, Key=test_key)
        downloaded_content = response['Body'].read().decode('utf-8')
        
        if downloaded_content == test_content:
            print("✅ Test file content verified!")
        else:
            print("❌ Test file content mismatch")
            
        # Clean up test file
        s3_client.delete_object(Bucket=bucket_name, Key=test_key)
        print("✅ Test file cleaned up")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"❌ Upload failed with error: {error_code}")
        print(f"Error message: {e.response['Error']['Message']}")
        
        if error_code == 'NoSuchBucket':
            print("💡 The bucket doesn't exist. You need to create it first.")
        elif error_code == 'AccessDenied':
            print("💡 Access denied. Check your IAM permissions.")
            
        return False
    except Exception as e:
        print(f"❌ Unexpected error during upload: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 AWS Connection Test for eu-north-1 Region")
    print("=" * 60)
    
    # Test 1: Check credentials
    test_aws_credentials()
    
    # Test 2: Test S3 connection
    s3_success = test_s3_connection()
    
    if s3_success:
        # Test 3: Test bucket access
        bucket_success = test_bucket_access()
        
        if bucket_success:
            # Test 4: Test upload capability
            test_s3_upload()
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
