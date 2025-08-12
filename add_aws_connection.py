#!/usr/bin/env python3
"""
Add AWS connection to Airflow for eu-north-1 region
"""

def add_aws_connection():
    """Add AWS connection via Airflow CLI"""
    print("🔧 Adding AWS connection to Airflow...")
    print("=" * 50)
    
    print("""
📋 To add the AWS connection, you need your:
1. AWS Access Key ID (from your IAM user)
2. AWS Secret Access Key (from your IAM user)

💡 If you don't have these, go to AWS Console → IAM → Users → your-threat-intel-user → Security credentials → Create access key
""")
    
    # Get credentials from user input
    print("Please enter your AWS credentials:")
    access_key = input("AWS Access Key ID: ").strip()
    secret_key = input("AWS Secret Access Key: ").strip()
    
    if not access_key or not secret_key:
        print("❌ Both Access Key ID and Secret Access Key are required!")
        return False
    
    # Create connection command
    connection_cmd = f"""airflow connections add aws_default \\
    --conn-type aws \\
    --login '{access_key}' \\
    --password '{secret_key}' \\
    --extra '{{"region_name": "eu-north-1"}}'"""
    
    print(f"\n🚀 Connection command:")
    print(f"```")
    print(connection_cmd)
    print(f"```")
    
    print(f"\n💡 To add this connection, run:")
    print(f"docker-compose exec airflow-worker bash -c \"{connection_cmd}\"")
    
    return True

if __name__ == "__main__":
    add_aws_connection()
