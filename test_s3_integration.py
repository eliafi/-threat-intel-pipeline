"""
Test script to validate S3 integration setup
Run this after setting up AWS credentials to test the connection
"""

import os
import sys
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

def test_aws_credentials():
    """Test if AWS credentials are properly configured"""
    print("🔍 Testing AWS credentials...")
    
    try:
        # Create S3 client
        s3_client = boto3.client('s3')
        
        # Try to list buckets (this requires minimal permissions)
        response = s3_client.list_buckets()
        print("✅ AWS credentials are working!")
        print(f"📊 Found {len(response['Buckets'])} S3 buckets in your account")
        
        return True
        
    except NoCredentialsError:
        print("❌ AWS credentials not found!")
        print("💡 Set up credentials using one of these methods:")
        print("   1. AWS CLI: aws configure")
        print("   2. Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
        print("   3. IAM role (for EC2 instances)")
        return False
        
    except ClientError as e:
        print(f"❌ AWS error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_s3_bucket_access(bucket_name="threat-intel-data-lake"):
    """Test if we can access/create the specified S3 bucket"""
    print(f"\n🪣 Testing S3 bucket access: {bucket_name}")
    
    try:
        s3_client = boto3.client('s3')
        
        # Check if bucket exists
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            print(f"✅ Bucket '{bucket_name}' exists and is accessible!")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == '404':
                print(f"📝 Bucket '{bucket_name}' doesn't exist")
                print("💡 The pipeline will create it automatically when needed")
                return True
                
            elif error_code == '403':
                print(f"❌ Access denied to bucket '{bucket_name}'")
                print("💡 Check your IAM permissions for S3 access")
                return False
                
            else:
                print(f"❌ Error accessing bucket: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Unexpected error testing bucket: {e}")
        return False

def test_file_upload(bucket_name="threat-intel-data-lake"):
    """Test uploading a small test file to S3"""
    print(f"\n📤 Testing file upload to S3...")
    
    try:
        s3_client = boto3.client('s3')
        
        # Create a test file content
        test_content = "This is a test file for threat intel pipeline"
        test_key = "test/pipeline_test.txt"
        
        # Upload test file
        s3_client.put_object(
            Bucket=bucket_name,
            Key=test_key,
            Body=test_content.encode('utf-8')
        )
        
        print(f"✅ Successfully uploaded test file to s3://{bucket_name}/{test_key}")
        
        # Clean up - delete test file
        s3_client.delete_object(Bucket=bucket_name, Key=test_key)
        print("🧹 Cleaned up test file")
        
        return True
        
    except ClientError as e:
        print(f"❌ Upload failed: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error during upload: {e}")
        return False

def main():
    """Run all S3 integration tests"""
    print("🧪 S3 Integration Test Suite")
    print("=" * 40)
    
    # Test 1: AWS Credentials
    creds_ok = test_aws_credentials()
    
    if not creds_ok:
        print("\n❌ Cannot proceed without valid AWS credentials")
        sys.exit(1)
    
    # Test 2: Bucket Access
    bucket_access_ok = test_s3_bucket_access()
    
    # Test 3: File Upload (only if bucket access is OK)
    upload_ok = False
    if bucket_access_ok:
        upload_ok = test_file_upload()
    
    # Summary
    print("\n" + "=" * 40)
    print("📋 Test Summary:")
    print(f"   AWS Credentials: {'✅' if creds_ok else '❌'}")
    print(f"   Bucket Access:   {'✅' if bucket_access_ok else '❌'}")
    print(f"   File Upload:     {'✅' if upload_ok else '❌'}")
    
    if all([creds_ok, bucket_access_ok, upload_ok]):
        print("\n🎉 All tests passed! Your S3 integration is ready!")
        print("🚀 You can now run your threat intelligence DAG with S3 upload")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues before proceeding.")
        print("📚 Check docs/S3_SETUP.md for detailed setup instructions")

if __name__ == "__main__":
    main()
