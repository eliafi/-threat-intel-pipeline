#!/usr/bin/env python3

import boto3
from botocore.exceptions import NoCredentialsError, ClientError

def test_aws_credentials():
    print("🔍 Testing AWS credentials...")
    try:
        s3 = boto3.client('s3')
        buckets = s3.list_buckets()
        print(f"✅ AWS credentials work! Found {len(buckets['Buckets'])} buckets")
        return True
    except NoCredentialsError:
        print("❌ No AWS credentials found")
        return False
    except ClientError as e:
        print(f"❌ AWS error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_aws_credentials()
