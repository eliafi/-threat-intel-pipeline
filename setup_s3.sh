#!/bin/bash

# S3 Integration Setup Script for Threat Intelligence Pipeline

echo "🚀 Setting up S3 integration for Threat Intelligence Pipeline..."

# Step 1: Restart Docker containers to install new packages
echo "📦 Restarting Docker containers to install boto3 and AWS providers..."
cd "$(dirname "$0")"

# Stop containers
docker-compose down

# Start containers (this will install new packages)
docker-compose up -d

echo "⏳ Waiting for Airflow to start (this may take 2-3 minutes)..."
sleep 120

# Check if Airflow is running
echo "🔍 Checking Airflow status..."
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ Airflow is running!"
else
    echo "❌ Airflow is not responding. Please check docker logs."
    exit 1
fi

echo ""
echo "🎯 Next Steps:"
echo "1. Set up AWS credentials (see docs/S3_SETUP.md)"
echo "2. Configure Airflow connection at http://localhost:8080/connection/add"
echo "3. Run your DAG to test S3 upload"
echo ""
echo "📚 For detailed instructions, see: docs/S3_SETUP.md"
echo ""
echo "🔧 Quick setup:"
echo "   - Connection ID: aws_default"
echo "   - Connection Type: Amazon Web Services"
echo "   - Login: Your AWS Access Key ID"
echo "   - Password: Your AWS Secret Access Key"
echo "   - Extra: {\"region_name\": \"us-east-1\"}"
