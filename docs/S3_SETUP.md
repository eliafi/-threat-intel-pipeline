# AWS S3 Setup Guide for Threat Intelligence Pipeline

## Overview
This guide will help you set up AWS S3 integration for your threat intelligence pipeline.

## Prerequisites
1. AWS Account
2. AWS Access Key ID and Secret Access Key
3. S3 bucket (will be created automatically if it doesn't exist)

## Step 1: Get AWS Credentials

### Option A: Using AWS IAM User (Recommended for development)
1. Go to AWS Console → IAM → Users
2. Create a new user or use existing user
3. Attach the following policy (or create a custom policy):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket",
                "s3:CreateBucket",
                "s3:GetBucketLocation"
            ],
            "Resource": [
                "arn:aws:s3:::threat-intel-data-lake",
                "arn:aws:s3:::threat-intel-data-lake/*"
            ]
        }
    ]
}
```

4. Generate Access Key ID and Secret Access Key

### Option B: Using AWS CLI Profile
1. Install AWS CLI: `pip install awscli`
2. Configure: `aws configure`
3. Enter your credentials when prompted

## Step 2: Configure Airflow Connection

### Method 1: Via Airflow Web UI (Recommended)
1. Open Airflow UI: http://localhost:8080
2. Go to Admin → Connections
3. Click "+" to add new connection
4. Fill in the details:
   - **Connection Id**: `aws_default`
   - **Connection Type**: `Amazon Web Services`
   - **Login**: Your AWS Access Key ID
   - **Password**: Your AWS Secret Access Key
   - **Extra**: `{"region_name": "us-east-1"}` (change region if needed)

### Method 2: Via Environment Variables
Add to your docker-compose.yaml under the environment section:

```yaml
environment:
  AWS_DEFAULT_REGION: us-east-1
  AWS_ACCESS_KEY_ID: your_access_key_here
  AWS_SECRET_ACCESS_KEY: your_secret_key_here
```

## Step 3: Configure S3 Bucket Settings

### Via Airflow Variables (Optional)
1. Go to Admin → Variables in Airflow UI
2. Add these variables:
   - **Key**: `S3_BUCKET_NAME`, **Value**: `your-custom-bucket-name`
   - **Key**: `AWS_CONN_ID`, **Value**: `aws_default`

### Default Settings
If you don't set variables, the pipeline will use:
- Bucket: `threat-intel-data-lake`
- Connection: `aws_default`
- Region: `us-east-1`

## Step 4: S3 Bucket Structure

Your files will be organized as:
```
threat-intel-data-lake/
├── threat-intel/
│   └── processed/
│       ├── 2025/
│       │   ├── 08/
│       │   │   ├── 08/
│       │   │   │   ├── otx_pulses_20250808_152112_processed.csv
│       │   │   │   └── otx_pulses_20250808_163045_processed.csv
│       │   │   └── 09/
│       │   └── 09/
│       └── 2025/
```

## Security Best Practices

1. **Use IAM Roles**: For production, use IAM roles instead of access keys
2. **Least Privilege**: Only grant necessary S3 permissions
3. **Bucket Policies**: Add bucket policies for additional security
4. **Encryption**: Enable S3 server-side encryption
5. **Access Logging**: Enable S3 access logging for audit trails

## Troubleshooting

### Common Issues:
1. **Permission Denied**: Check IAM permissions and bucket policies
2. **Region Mismatch**: Ensure region in connection matches bucket region
3. **Bucket Not Found**: Pipeline will create bucket automatically if permissions allow

### Testing Connection:
```python
# Test in Airflow UI → Admin → Connections → Test
# Or add a test task to your DAG
```

## Cost Considerations

- S3 Standard storage: ~$0.023 per GB/month
- PUT requests: ~$0.005 per 1,000 requests
- For typical threat intel data (1-10 MB files daily): <$1/month

## Next Steps

1. Set up AWS credentials
2. Configure Airflow connection
3. Restart Docker containers
4. Run your DAG to test S3 upload
5. Verify files appear in S3 console
