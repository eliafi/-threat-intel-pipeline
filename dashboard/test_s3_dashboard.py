#!/usr/bin/env python3
"""
Test script to verify S3 connection from dashboard container
"""
import boto3
import os
from botocore.exceptions import ClientError, NoCredentialsError

def test_s3_connection():
    """Test S3 connection using environment variables"""
    
    print("🔍 Testing S3 Connection...")
    print(f"AWS_ACCESS_KEY_ID: {os.getenv('AWS_ACCESS_KEY_ID', 'NOT SET')}")
    print(f"AWS_SECRET_ACCESS_KEY: {'SET' if os.getenv('AWS_SECRET_ACCESS_KEY') else 'NOT SET'}")
    print(f"AWS_DEFAULT_REGION: {os.getenv('AWS_DEFAULT_REGION', 'NOT SET')}")
    print()
    
    bucket_name = "threat-intel-data-lake"
    region = "eu-north-1"
    
    try:
        # Create S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_DEFAULT_REGION', region)
        )
        
        # Test bucket access
        print(f"🔍 Testing access to bucket: {bucket_name}")
        s3_client.head_bucket(Bucket=bucket_name)
        print("✅ Bucket access successful!")
        
        # List objects
        print(f"📁 Listing objects in bucket...")
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix='threat-intel/'
        )
        
        if 'Contents' in response:
            files = [obj['Key'] for obj in response['Contents'] if obj['Key'].endswith('.csv')]
            print(f"✅ Found {len(files)} CSV files:")
            for file in files[:5]:  # Show first 5 files
                print(f"   - {file}")
            if len(files) > 5:
                print(f"   ... and {len(files) - 5} more files")
        else:
            print("⚠️  No files found in threat-intel/ prefix")
        
        print("\n🎉 S3 connection test successful!")
        return True
        
    except NoCredentialsError:
        print("❌ AWS credentials not found or invalid")
        return False
    except ClientError as e:
        print(f"❌ AWS Client Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_s3_connection()
