# AWS S3 Setup Guide for Threat Intelligence Pipeline

## Overview
This guide will help you set up AWS S3 integration for your threat intelligence pipeline. We'll walk through creating an S3 bucket, setting up IAM permissions, and configuring Airflow connections step-by-step.

## Prerequisites
1. AWS Account (free tier is sufficient for testing)
2. Access to AWS Console
3. Basic understanding of AWS services

## Step 1: Create an S3 Bucket

### 1.1 Log into AWS Console
1. Open your web browser and go to https://console.aws.amazon.com/
2. Click "Sign In" and enter your AWS account credentials
3. Once logged in, you'll see the AWS Management Console dashboard

### 1.2 Navigate to S3 Service
1. In the AWS Console, look for the search bar at the top
2. Type "S3" and press Enter
3. Click on "S3" under Services (it should be the first result)
4. You'll now see the Amazon S3 console

### 1.3 Create Your Bucket
1. Click the orange **"Create bucket"** button on the right side
2. You'll be taken to the "Create bucket" configuration page

### 1.4 Configure Bucket Settings

#### Basic Configuration:
- **Bucket name**: Enter `threat-intel-pipeline` (or choose your own unique name)
  - ⚠️ **Important**: Bucket names must be globally unique across all AWS accounts
  - If your name is taken, try: `threat-intel-pipeline-yourname` or `threat-intel-pipeline-2025`
- **AWS Region**: Select **Europe (Stockholm) eu-north-1**
  - ⚠️ **Important**: Use eu-north-1 region for this setup
  - Other popular regions for reference:
    - US East (N. Virginia) us-east-1
    - US West (Oregon) us-west-2
    - Europe (Ireland) eu-west-1

#### Object Ownership (keep defaults):
- Select **"ACLs disabled (recommended)"**

#### Block Public Access Settings (IMPORTANT - keep these enabled):
- ✅ **"Block all public access"** - Keep this checked for security
- This ensures your threat intelligence data stays private

#### Bucket Versioning (optional):
- Choose **"Disable"** for now (you can enable later if needed)
- Versioning keeps multiple versions of files but costs more

#### Default Encryption (recommended):
- Select **"Enable"**
- Choose **"Amazon S3 managed keys (SSE-S3)"**
- This encrypts your data at rest for security

#### Advanced Settings (optional):
- **Object Lock**: Leave disabled
- **Tags**: You can add tags like:
  - Key: `Project`, Value: `ThreatIntel`
  - Key: `Environment`, Value: `Development`

### 1.5 Create the Bucket
1. Scroll down to the bottom of the page
2. Click the orange **"Create bucket"** button
3. You should see a green success message: "Successfully created bucket 'your-bucket-name'"
4. You'll be redirected back to the S3 buckets list, where you can see your new bucket

### 1.6 Verify Bucket Creation
1. Look for your bucket in the list (it should appear immediately)
2. Click on your bucket name to open it
3. You should see an empty bucket with folders like: "Objects", "Properties", "Permissions", etc.
4. Note your bucket name - you'll need it for Airflow configuration

## Step 2: Create IAM User and Get Access Keys

## Step 2: Create IAM User and Get Access Keys

### 2.1 Navigate to IAM Service
1. In the AWS Console search bar, type "IAM"
2. Click on "IAM" under Services
3. You'll see the IAM (Identity and Access Management) dashboard

### 2.2 Create a New User
1. In the left sidebar, click **"Users"**
2. Click the **"Create user"** button (blue button on the right)
3. Enter user details:
   - **User name**: `threat-intel-pipeline-user` (or your preferred name)
   - **Provide user access to the AWS Management Console**: Leave unchecked (we only need programmatic access)
4. Click **"Next"**

### 2.3 Set Permissions
You have two options for permissions:

#### Option A: Attach Existing Policy (Easier but broader permissions)
1. Select **"Attach policies directly"**
2. In the search box, type "S3"
3. Check the box next to **"AmazonS3FullAccess"**
4. Click **"Next"**

#### Option B: Create Custom Policy (More secure - recommended)
1. Select **"Create inline policy"**
2. Click on the **"JSON"** tab
3. Replace the default content with this policy:

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

4. Replace `threat-intel-data-lake` with your actual bucket name if different
5. Click **"Next"**
6. Give the policy a name: `ThreatIntelS3Access`
7. Click **"Create policy"**

### 2.4 Review and Create User
1. Review the user settings
2. Click **"Create user"**
3. You should see a success message

### 2.5 Create Access Keys
1. Click on your newly created user name in the users list
2. Click on the **"Security credentials"** tab
3. Scroll down to **"Access keys"** section
4. Click **"Create access key"**
5. Select **"Application running outside AWS"**
6. Click **"Next"**
7. (Optional) Add a description: "Threat Intel Pipeline Access"
8. Click **"Create access key"**

### 2.6 Save Your Credentials (IMPORTANT!)
⚠️ **CRITICAL**: You'll only see the secret key once!

1. You'll see a page with:
   - **Access key ID**: Something like `AKIAIOSFODNN7EXAMPLE`
   - **Secret access key**: Something like `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`

2. **SAVE THESE IMMEDIATELY**:
   - Click **"Download .csv file"** to save them securely
   - Or copy them to a secure password manager
   - Or write them down securely

3. Click **"Done"**

**Security Note**: Treat these credentials like passwords. Never share them or commit them to code repositories.

## Step 3: Configure Airflow Connection

Now you'll connect your AWS credentials to Airflow so the pipeline can upload files to S3.

### 3.1 Start Your Airflow Environment
1. Open PowerShell or Command Prompt
2. Navigate to your project directory:
   ```bash
   cd "c:\Users\HP\Desktop\Threat Intel Pipeline"
   ```
3. Make sure Docker is running, then start Airflow:
   ```bash
   docker-compose up -d
   ```
4. Wait 2-3 minutes for all services to start

### 3.2 Access Airflow Web Interface
1. Open your web browser
2. Go to: http://localhost:8080
3. Login with:
   - **Username**: `airflow`
   - **Password**: `airflow`

### 3.3 Create AWS Connection
1. In Airflow, click **"Admin"** in the top menu
2. Select **"Connections"** from the dropdown
3. Click the **"+"** button to add a new connection
4. Fill in the connection details:

   - **Connection Id**: `aws_default`
   - **Connection Type**: Select **"Amazon Web Services"** from dropdown
   - **Login**: Paste your **Access Key ID** (from Step 2.6)
   - **Password**: Paste your **Secret Access Key** (from Step 2.6)
   - **Extra**: Enter this JSON (replace `us-east-1` with your bucket's region):
     ```json
     {"region_name": "us-east-1"}
     ```

5. Click **"Save"** button

### 3.4 Test the Connection
1. After saving, you should see your connection in the list
2. Click the **"Test"** button next to your connection (if available)
3. You should see a green checkmark if successful

### 3.5 Configure Bucket Name (Optional)
If you used a different bucket name than `threat-intel-data-lake`:

1. In Airflow, go to **"Admin"** → **"Variables"**
2. Click **"+"** to add a new variable
3. Create this variable:
   - **Key**: `S3_BUCKET_NAME`
   - **Value**: Your actual bucket name (e.g., `threat-intel-data-lake-yourname`)
4. Click **"Save"**

## Step 4: Test Your S3 Integration

### 4.1 Run the Test Script

**Important**: Since you're using Docker, you need to run the test script inside the Airflow container where Python and the required packages are available.

1. Open PowerShell in your project directory
2. Copy the test script to the dags folder (so it's accessible from the container):
   ```powershell
   copy test_s3_integration.py dags\
   ```
3. Run the test script inside the Airflow container:
   ```powershell
   docker-compose exec airflow-worker python /opt/airflow/dags/test_s3_integration.py
   ```
4. You should see output like:
   ```
   🧪 S3 Integration Test Suite
   ========================================
   🔍 Testing AWS credentials...
   ✅ AWS credentials are working!
   📊 Found X S3 buckets in your account
   
   🪣 Testing S3 bucket access: threat-intel-data-lake
   ✅ Bucket 'threat-intel-data-lake' exists and is accessible!
   
   📤 Testing file upload to S3...
   ✅ Successfully uploaded test file to s3://threat-intel-data-lake/test/pipeline_test.txt
   🧹 Cleaned up test file
   
   ========================================
   📋 Test Summary:
      AWS Credentials: ✅
      Bucket Access:   ✅
      File Upload:     ✅
   
   🎉 All tests passed! Your S3 integration is ready!
   ```

### 4.2 Run Your Pipeline
1. In Airflow UI (http://localhost:8080), go to **"DAGs"**
2. Find your **"threat_intel_pipeline"** DAG
3. Click the **toggle switch** to enable it if it's disabled
4. Click the **"play"** button (▶️) to trigger it manually
5. Watch the pipeline run through all 3 steps:
   - **fetch_otx_data**: Downloads threat intelligence
   - **transform_data**: Converts to CSV format
   - **upload_to_s3**: Uploads to your S3 bucket

### 4.3 Verify Files in S3
1. Go back to AWS Console → S3
2. Click on your bucket name
3. Navigate to: `threat-intel/processed/2025/08/12/` (or current date)
4. You should see your CSV files uploaded there!

## Step 5: Monitor and Maintain

## Step 5: Monitor and Maintain

### 5.1 Monitor Your Pipeline
- Check Airflow logs for any S3 upload errors
- Monitor your AWS billing (S3 costs are very low for this use case)
- Set up CloudWatch alerts if needed

### 5.2 View Your Data
- Files are organized by date: `threat-intel/processed/YYYY/MM/DD/`
- Each CSV file contains threat intelligence data with IOCs
- You can download files directly from S3 console or use AWS CLI

### 5.3 Security Best Practices
- Regularly rotate your access keys
- Monitor AWS CloudTrail for access logs
- Consider using IAM roles instead of access keys for production
- Enable S3 bucket logging if needed

## Troubleshooting Common Issues

### "Access Denied" Error
- **Check**: IAM permissions are correct
- **Check**: Bucket name in Airflow variable matches actual bucket
- **Check**: Region in Airflow connection matches bucket region

### "Bucket Not Found" Error  
- **Check**: Bucket name is spelled correctly
- **Check**: You're in the right AWS region
- **Solution**: Pipeline will try to create bucket automatically

### "Credentials Not Found" Error
- **Check**: AWS connection is saved in Airflow
- **Check**: Connection ID is exactly `aws_default`
- **Check**: Access keys are entered correctly (no extra spaces)

### Pipeline Fails at S3 Upload Step
1. Check Airflow logs for detailed error message
2. Test credentials with: `python test_s3_integration.py`
3. Verify bucket exists and you have permissions

### Files Not Appearing in S3
- **Check**: Pipeline completed successfully
- **Check**: Looking in correct bucket and date path
- **Wait**: Sometimes S3 takes a few seconds to show new files

## Summary

You've now set up:
1. ✅ S3 bucket for threat intelligence data storage
2. ✅ IAM user with proper permissions
3. ✅ Airflow connection to AWS
4. ✅ Complete ETL pipeline: Fetch → Transform → Store in S3

Your threat intelligence data will now be automatically stored in AWS S3, creating a searchable data lake that can integrate with other AWS services for advanced analytics.

## Next Steps
- Set up automated scheduling for your pipeline
- Explore AWS Athena for querying your threat data
- Consider AWS QuickSight for threat intelligence dashboards
- Set up AWS Lambda for real-time threat processing

## Support
- Check project documentation in the `docs/` folder
- Review Airflow logs for troubleshooting
- AWS documentation: https://docs.aws.amazon.com/s3/
