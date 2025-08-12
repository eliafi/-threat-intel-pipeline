#!/usr/bin/env python3
"""
Simple AWS connection test
"""
print("🔍 Testing AWS Connection...")

# Test 1: Check environment variables
import os
access_key = os.environ.get('AWS_ACCESS_KEY_ID')
secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

if access_key and secret_key:
    print(f"✅ Environment variables found: {access_key[:8]}...")
else:
    print("❌ No environment variables found")

# Test 2: Check Airflow connection
try:
    from airflow.hooks.base import BaseHook
    conn = BaseHook.get_connection('aws_default')
    if conn.login and conn.password:
        print(f"✅ Airflow connection found: {conn.login[:8]}...")
    else:
        print("❌ Airflow connection not found or incomplete")
except Exception as e:
    print(f"❌ Airflow connection error: {e}")

# Test 3: Try boto3
try:
    import boto3
    s3 = boto3.client('s3', region_name='eu-north-1')
    response = s3.list_buckets()
    print(f"✅ S3 connection successful! Found {len(response['Buckets'])} buckets")
    for bucket in response['Buckets']:
        print(f"  - {bucket['Name']}")
except Exception as e:
    print(f"❌ S3 connection failed: {e}")

print("🏁 Test completed!")
