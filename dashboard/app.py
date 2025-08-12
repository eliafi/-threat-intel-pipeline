"""
Enhanced Threat Intelligence Dashboard
Integrates with your existing Airflow + S3 pipeline
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError
import json
import os

# Configure page
st.set_page_config(
    page_title="Threat Intel Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

class ThreatIntelDashboard:
    def __init__(self):
        self.bucket_name = "threat-intel-data-lake"
        self.region = "eu-north-1"
        self.s3_client = None
        self.init_aws_connection()
    
    def init_aws_connection(self):
        """Initialize AWS connection using your existing credentials"""
        try:
            # Try to use the same AWS credentials as your Airflow setup
            self.s3_client = boto3.client('s3', region_name=self.region)
            # Test connection
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
        except Exception as e:
            st.error(f"❌ AWS Connection Failed: {e}")
            st.info("💡 Make sure your AWS credentials are configured")
            return False
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def list_available_files(_self):
        """List all processed CSV files in S3"""
        try:
            response = _self.s3_client.list_objects_v2(
                Bucket=_self.bucket_name,
                Prefix='threat-intel/processed/'
            )
            
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    if obj['Key'].endswith('.csv'):
                        files.append({
                            'key': obj['Key'],
                            'filename': obj['Key'].split('/')[-1],
                            'last_modified': obj['LastModified'],
                            'size': obj['Size']
                        })
            
            # Sort by last modified (newest first)
            files.sort(key=lambda x: x['last_modified'], reverse=True)
            return files
            
        except Exception as e:
            st.error(f"Error listing files: {e}")
            return []
    
    @st.cache_data(ttl=300, show_spinner=False)  # Cache for 5 minutes with file-specific key
    def load_data_from_s3(_self, s3_key: str):
        """Load CSV data from S3 - cached per file"""
        try:
            # Include the s3_key in the cache to ensure different files get different cache entries
            response = _self.s3_client.get_object(
                Bucket=_self.bucket_name,
                Key=s3_key
            )
            df = pd.read_csv(response['Body'])
            # Add metadata to help with debugging
            st.info(f"🔄 Loaded fresh data from: {s3_key.split('/')[-1]} ({len(df)} records)")
            return df
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return None
    
    def render_sidebar(self):
        """Render sidebar with file selection and filters"""
        st.sidebar.title("🛡️ Threat Intel Dashboard")
        st.sidebar.markdown("---")
        
        # Cache management
        st.sidebar.subheader("🔄 Cache Management")
        if st.sidebar.button("Clear Data Cache", help="Clear cached data to force reload"):
            st.cache_data.clear()
            st.sidebar.success("Cache cleared!")
            st.rerun()
        
        # File selection
        st.sidebar.subheader("📁 Data Selection")
        available_files = self.list_available_files()
        
        if not available_files:
            st.sidebar.warning("No data files found in S3")
            return None
        
        file_options = {
            f"{file['filename']} ({file['last_modified'].strftime('%Y-%m-%d %H:%M')})": file['key']
            for file in available_files
        }
        
        selected_file_display = st.sidebar.selectbox(
            "Select Data File:",
            options=list(file_options.keys()),
            help="Choose the threat intelligence data file to analyze"
        )
        
        if selected_file_display:
            return file_options[selected_file_display]
        return None
    
    def render_overview_metrics(self, df):
        """Render overview metrics cards"""
        st.subheader("📊 Overview Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Indicators",
                value=len(df),
                help="Total number of threat indicators"
            )
        
        with col2:
            unique_ips = df['indicators.IPv4'].nunique() if 'indicators.IPv4' in df.columns else 0
            st.metric(
                label="Unique IPs",
                value=unique_ips,
                help="Number of unique IP addresses"
            )
        
        with col3:
            unique_domains = df['indicators.domain'].nunique() if 'indicators.domain' in df.columns else 0
            st.metric(
                label="Unique Domains",
                value=unique_domains,
                help="Number of unique domains"
            )
        
        with col4:
            unique_tags = len(set([tag for tags in df.get('tags', []) if isinstance(tags, str) for tag in tags.split(',')])) if 'tags' in df.columns else 0
            st.metric(
                label="Unique Tags",
                value=unique_tags,
                help="Number of unique threat tags"
            )
    
    def render_threat_timeline(self, df):
        """Render threat detection timeline"""
        st.subheader("📈 Threat Detection Timeline")
        
        if 'created' in df.columns:
            # Convert created column to datetime
            df['created_date'] = pd.to_datetime(df['created'], errors='coerce')
            df['date'] = df['created_date'].dt.date
            
            # Group by date and count
            timeline_data = df.groupby('date').size().reset_index(name='count')
            
            # Create timeline chart
            fig = px.line(
                timeline_data,
                x='date',
                y='count',
                title="Threats Detected Over Time",
                labels={'count': 'Number of Threats', 'date': 'Date'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Timeline data not available in this dataset")
    
    def render_threat_categories(self, df):
        """Render threat categories analysis"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏷️ Threat Categories")
            if 'tags' in df.columns:
                # Extract and count tags
                all_tags = []
                for tags in df['tags'].dropna():
                    if isinstance(tags, str):
                        all_tags.extend([tag.strip() for tag in tags.split(',')])
                
                if all_tags:
                    tag_counts = pd.Series(all_tags).value_counts().head(10)
                    fig = px.bar(
                        x=tag_counts.values,
                        y=tag_counts.index,
                        orientation='h',
                        title="Top 10 Threat Tags"
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No tags data available")
            else:
                st.info("Tags column not found in dataset")
        
        with col2:
            st.subheader("🌍 Geographic Distribution")
            if 'indicators.IPv4' in df.columns:
                # For demo purposes - in real scenario you'd use IP geolocation
                ip_sample = df['indicators.IPv4'].dropna().head(100)
                st.info(f"Found {len(ip_sample)} IP indicators")
                st.text("Geographic mapping would require IP geolocation service")
            else:
                st.info("IP address data not available")
    
    def render_detailed_table(self, df):
        """Render detailed data table with filtering"""
        st.subheader("🔍 Detailed Threat Data")
        
        # Add filters
        col1, col2 = st.columns(2)
        
        with col1:
            # Date filter
            if 'created' in df.columns:
                df['created_date'] = pd.to_datetime(df['created'], errors='coerce')
                min_date = df['created_date'].min().date()
                max_date = df['created_date'].max().date()
                
                date_range = st.date_input(
                    "Date Range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date
                )
                
                if len(date_range) == 2:
                    mask = (df['created_date'].dt.date >= date_range[0]) & (df['created_date'].dt.date <= date_range[1])
                    df = df[mask]
        
        with col2:
            # Tag filter
            if 'tags' in df.columns:
                all_tags = set()
                for tags in df['tags'].dropna():
                    if isinstance(tags, str):
                        all_tags.update([tag.strip() for tag in tags.split(',')])
                
                if all_tags:
                    selected_tags = st.multiselect(
                        "Filter by Tags",
                        options=sorted(list(all_tags)),
                        help="Select tags to filter the data"
                    )
                    
                    if selected_tags:
                        mask = df['tags'].str.contains('|'.join(selected_tags), na=False)
                        df = df[mask]
        
        # Display table
        st.dataframe(
            df.head(1000),  # Limit to 1000 rows for performance
            use_container_width=True,
            height=400
        )
        
        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name=f"threat_intel_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

def main():
    """Main dashboard application"""
    
    # Initialize session state for file tracking
    if 'current_file' not in st.session_state:
        st.session_state.current_file = None
    
    # Initialize dashboard
    dashboard = ThreatIntelDashboard()
    
    # Render sidebar and get selected file
    selected_file_key = dashboard.render_sidebar()
    
    # Check if file changed and clear cache if needed
    if selected_file_key != st.session_state.current_file:
        # Clear the cache when switching files
        st.cache_data.clear()
        st.session_state.current_file = selected_file_key
        # Force a rerun to ensure fresh data is loaded
        if st.session_state.current_file is not None:
            st.rerun()
    
    if not selected_file_key:
        st.info("👆 Please select a data file from the sidebar to begin analysis")
        st.markdown("""
        ### 🚀 Welcome to the Threat Intelligence Dashboard
        
        This dashboard displays threat intelligence data processed by your Airflow pipeline:
        
        - **📊 Overview Metrics**: Key statistics about your threat data
        - **📈 Timeline Analysis**: Threat detection trends over time  
        - **🏷️ Category Analysis**: Breakdown of threat types and tags
        - **🔍 Detailed View**: Searchable and filterable data table
        
        **Data Source**: `threat-intel-data-lake` S3 bucket (eu-north-1)
        """)
        return
    
    # Load selected data
    with st.spinner(f"Loading data from {selected_file_key.split('/')[-1]}..."):
        df = dashboard.load_data_from_s3(selected_file_key)
    
    if df is None:
        st.error("Failed to load data. Please check your AWS connection.")
        return
    
    if df.empty:
        st.warning("The selected file contains no data.")
        return
    
    # Main dashboard content
    st.title("🛡️ Threat Intelligence Dashboard")
    st.markdown(f"**Data Source**: `{selected_file_key.split('/')[-1]}` | **Records**: {len(df):,}")
    st.markdown("---")
    
    # Render dashboard sections
    dashboard.render_overview_metrics(df)
    st.markdown("---")
    
    dashboard.render_threat_timeline(df)
    st.markdown("---")
    
    dashboard.render_threat_categories(df)
    st.markdown("---")
    
    dashboard.render_detailed_table(df)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.8em;'>
        🛡️ Threat Intelligence Dashboard | Powered by Streamlit + AWS S3 + Airflow
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
