#!/usr/bin/env python3
"""
Create S3 bucket for threat intelligence pipeline in eu-north-1 region
"""
import boto3
from botocore.exceptions import ClientError

def create_bucket():
    """Create the threat-intel-pipeline bucket in eu-north-1"""
    bucket_name = 'threat-intel-pipeline'
    region = 'eu-north-1'
    
    print(f"🚀 Creating S3 bucket '{bucket_name}' in region '{region}'...")
    
    try:
        # Create S3 client
        s3_client = boto3.client('s3', region_name=region)
        
        # Check if bucket already exists
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            print(f"✅ Bucket '{bucket_name}' already exists!")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code != '404':
                print(f"❌ Error checking bucket: {error_code}")
                return False
        
        # Create bucket with region constraint
        if region != 'us-east-1':
            # For regions other than us-east-1, we need to specify location constraint
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        else:
            s3_client.create_bucket(Bucket=bucket_name)
        
        print(f"✅ Successfully created bucket '{bucket_name}' in {region}!")
        
        # Set up bucket versioning (recommended for data pipeline)
        print("🔧 Enabling bucket versioning...")
        s3_client.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        print("✅ Bucket versioning enabled!")
        
        # Set up server-side encryption
        print("🔧 Enabling server-side encryption...")
        s3_client.put_bucket_encryption(
            Bucket=bucket_name,
            ServerSideEncryptionConfiguration={
                'Rules': [
                    {
                        'ApplyServerSideEncryptionByDefault': {
                            'SSEAlgorithm': 'AES256'
                        }
                    }
                ]
            }
        )
        print("✅ Server-side encryption enabled!")
        
        # Set up lifecycle policy to manage costs
        print("🔧 Setting up lifecycle policy...")
        s3_client.put_bucket_lifecycle_configuration(
            Bucket=bucket_name,
            LifecycleConfiguration={
                'Rules': [
                    {
                        'ID': 'ThreatIntelDataLifecycle',
                        'Status': 'Enabled',
                        'Filter': {'Prefix': 'threat-intel/'},
                        'Transitions': [
                            {
                                'Days': 30,
                                'StorageClass': 'STANDARD_IA'
                            },
                            {
                                'Days': 90,
                                'StorageClass': 'GLACIER'
                            }
                        ]
                    }
                ]
            }
        )
        print("✅ Lifecycle policy configured!")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        if error_code == 'BucketAlreadyExists':
            print(f"❌ Bucket name '{bucket_name}' is already taken by another account")
        elif error_code == 'BucketAlreadyOwnedByYou':
            print(f"✅ Bucket '{bucket_name}' already exists and is owned by you")
            return True
        else:
            print(f"❌ Error creating bucket: {error_code}")
            print(f"Error message: {error_message}")
        
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_bucket_access():
    """Test access to the created bucket"""
    bucket_name = 'threat-intel-pipeline'
    region = 'eu-north-1'
    
    print(f"\n🔍 Testing access to bucket '{bucket_name}'...")
    
    try:
        s3_client = boto3.client('s3', region_name=region)
        
        # Test upload
        test_key = 'test/setup_test.txt'
        test_content = f"Bucket setup test - {bucket_name} in {region}"
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=test_key,
            Body=test_content.encode('utf-8'),
            ContentType='text/plain'
        )
        print(f"✅ Successfully uploaded test file!")
        
        # Test download
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
        
    except Exception as e:
        print(f"❌ Error testing bucket access: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("🪣 S3 Bucket Setup for Threat Intel Pipeline")
    print("=" * 60)
    
    # Create bucket
    success = create_bucket()
    
    if success:
        # Test bucket access
        test_bucket_access()
        print("\n✅ S3 bucket setup completed successfully!")
        print(f"Your bucket is ready at: s3://threat-intel-pipeline")
    else:
        print("\n❌ S3 bucket setup failed!")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
