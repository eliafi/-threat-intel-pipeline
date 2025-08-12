"""
Local Threat Intelligence Dashboard
Reads data from local CSV files instead of S3
"""
import http.server
import socketserver
import json
import os
import csv
from datetime import datetime
import webbrowser
import threading

class LocalDashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = self.create_dashboard_html()
            self.wfile.write(html.encode('utf-8'))
            
        elif self.path == '/data.json':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            data = self.get_local_data()
            self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))
        else:
            self.send_error(404)
    
    def get_local_data(self):
        """Get threat intelligence data from local CSV files"""
        data_dir = "/opt/airflow/data"
        result = {
            "timestamp": datetime.now().isoformat(),
            "files": [],
            "summary": {
                "total_files": 0,
                "total_records": 0,
                "latest_file": None,
                "data_source": "Local Files"
            },
            "sample_data": [],
            "columns": []
        }
        
        try:
            if os.path.exists(data_dir):
                # Get all CSV files
                all_files = os.listdir(data_dir)
                csv_files = [f for f in all_files if f.endswith('.csv')]
                
                result["files"] = csv_files
                result["summary"]["total_files"] = len(csv_files)
                
                if csv_files:
                    # Get latest file by modification time
                    csv_files_with_time = [(f, os.path.getmtime(os.path.join(data_dir, f))) for f in csv_files]
                    latest_file = max(csv_files_with_time, key=lambda x: x[1])[0]
                    result["summary"]["latest_file"] = latest_file
                    
                    # Read sample data from latest file
                    latest_path = os.path.join(data_dir, latest_file)
                    try:
                        with open(latest_path, 'r', encoding='utf-8', errors='ignore') as f:
                            reader = csv.DictReader(f)
                            rows = list(reader)
                            
                            result["summary"]["total_records"] = len(rows)
                            result["sample_data"] = rows[:10]  # First 10 rows
                            result["columns"] = list(reader.fieldnames) if reader.fieldnames else []
                            
                    except Exception as e:
                        result["file_error"] = f"Error reading {latest_file}: {str(e)}"
                        
                else:
                    result["message"] = "No CSV files found in data directory"
                    
            else:
                result["error"] = f"Data directory '{data_dir}' not found"
                
        except Exception as e:
            result["error"] = f"Error accessing data: {str(e)}"
        
        return result
    
    def create_dashboard_html(self):
        """Create the local dashboard HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🛡️ Threat Intelligence Dashboard (Local)</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px;
        }
        .header { 
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        .header h1 { 
            font-size: 2.5em; 
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .metrics { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px;
        }
        .metric {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .metric-value { 
            font-size: 2.5em; 
            font-weight: bold; 
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 5px;
        }
        .metric-label { color: #666; font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px; }
        .card { 
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px; 
            padding: 25px; 
            margin-bottom: 25px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .card h3 { 
            margin-bottom: 20px; 
            color: #333;
            font-size: 1.3em;
        }
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin-top: 15px;
            background: white;
            border-radius: 10px;
            overflow: hidden;
        }
        th, td { 
            padding: 12px 15px; 
            text-align: left; 
            border-bottom: 1px solid #eee;
        }
        th { 
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            font-weight: 600;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        tr:hover { background: #f8f9fa; }
        .status { 
            padding: 8px 12px; 
            border-radius: 20px; 
            font-size: 0.9em; 
            font-weight: bold;
            display: inline-block;
            margin-bottom: 15px;
        }
        .status.success { background: #d4edda; color: #155724; }
        .status.error { background: #f8d7da; color: #721c24; }
        .status.warning { background: #fff3cd; color: #856404; }
        .status.info { background: #d1ecf1; color: #0c5460; }
        .refresh-btn {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-weight: bold;
            margin-bottom: 20px;
            transition: transform 0.2s;
        }
        .refresh-btn:hover { transform: translateY(-2px); }
        .loading { 
            text-align: center; 
            padding: 40px; 
            color: #666;
            font-style: italic;
        }
        .file-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .file-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        .file-name { font-weight: bold; margin-bottom: 5px; color: #333; }
        .file-details { color: #666; font-size: 0.9em; line-height: 1.4; }
        .pipeline-info {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .no-data { 
            text-align: center; 
            padding: 40px;
            background: #fff3cd;
            border-radius: 10px;
            margin: 20px 0;
        }
        .no-data h4 { color: #856404; margin-bottom: 15px; }
        .no-data p { color: #856404; line-height: 1.5; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ Threat Intelligence Dashboard</h1>
            <p>Local Data Analysis and Monitoring</p>
            <p><small>Reading from: <code>/opt/airflow/data/</code> • Last updated: <span id="last-update">Loading...</span></small></p>
        </div>
        
        <div class="pipeline-info">
            <strong>📍 Data Source:</strong> Local CSV files from your Airflow pipeline
        </div>
        
        <button class="refresh-btn" onclick="loadData()">🔄 Refresh Data</button>
        
        <div class="metrics">
            <div class="metric">
                <div class="metric-value" id="total-files">-</div>
                <div class="metric-label">CSV Files</div>
            </div>
            <div class="metric">
                <div class="metric-value" id="total-records">-</div>
                <div class="metric-label">Total Records</div>
            </div>
            <div class="metric">
                <div class="metric-value" id="columns-count">-</div>
                <div class="metric-label">Data Columns</div>
            </div>
            <div class="metric">
                <div class="metric-value" id="status-indicator">🔄</div>
                <div class="metric-label">Status</div>
            </div>
        </div>
        
        <div class="card">
            <h3>📊 Pipeline Data Status</h3>
            <div id="status-content">
                <div class="loading">Checking for threat intelligence data...</div>
            </div>
        </div>
        
        <div class="card">
            <h3>📁 Available Data Files</h3>
            <div id="files-content">
                <div class="loading">Loading files information...</div>
            </div>
        </div>
        
        <div class="card">
            <h3>📋 Sample Threat Data</h3>
            <div id="sample-content">
                <div class="loading">Loading sample data...</div>
            </div>
        </div>
    </div>

    <script>
        function loadData() {
            document.getElementById('status-indicator').textContent = '🔄';
            
            fetch('/data.json')
                .then(response => response.json())
                .then(data => {
                    updateDashboard(data);
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('status-indicator').textContent = '❌';
                    showError('Failed to load data: ' + error.message);
                });
        }
        
        function updateDashboard(data) {
            // Update timestamp
            document.getElementById('last-update').textContent = new Date().toLocaleString();
            
            // Update metrics
            document.getElementById('total-files').textContent = data.summary.total_files || 0;
            document.getElementById('total-records').textContent = data.summary.total_records || 0;
            document.getElementById('columns-count').textContent = data.columns ? data.columns.length : 0;
            
            // Update status
            if (data.error) {
                document.getElementById('status-indicator').textContent = '❌';
                showStatus('error', data.error);
                showError(data.error);
            } else if (data.files.length === 0) {
                document.getElementById('status-indicator').textContent = '⚠️';
                showNoPipelineData();
            } else {
                document.getElementById('status-indicator').textContent = '✅';
                showStatus('success', `Found ${data.files.length} data files with ${data.summary.total_records} total records`);
                showFiles(data.files, data.summary.latest_file);
                showSampleData(data.sample_data, data.columns);
            }
        }
        
        function showStatus(type, message) {
            const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : '⚠️';
            document.getElementById('status-content').innerHTML = 
                `<div class="status ${type}">${icon} ${message}</div>`;
        }
        
        function showNoPipelineData() {
            const content = `
                <div class="no-data">
                    <h4>⚠️ No threat intelligence data found</h4>
                    <p><strong>To generate data, please:</strong></p>
                    <p>1. Open Airflow UI: <a href="http://localhost:8080" target="_blank">http://localhost:8080</a></p>
                    <p>2. Run the <strong>threat_intel_pipeline</strong> DAG</p>
                    <p>3. Wait for the pipeline to complete</p>
                    <p>4. Refresh this dashboard</p>
                </div>
            `;
            
            document.getElementById('status-content').innerHTML = content;
            document.getElementById('files-content').innerHTML = content;
            document.getElementById('sample-content').innerHTML = 
                '<div class="status warning">⚠️ No sample data available - run the pipeline first</div>';
        }
        
        function showError(message) {
            document.getElementById('files-content').innerHTML = 
                `<div class="status error">❌ Error: ${message}</div>`;
            document.getElementById('sample-content').innerHTML = 
                `<div class="status error">❌ No sample data available due to error</div>`;
        }
        
        function showFiles(files, latestFile) {
            if (files.length === 0) {
                showNoPipelineData();
                return;
            }
            
            let html = `<div class="status success">✅ Found ${files.length} CSV files from your pipeline</div>`;
            html += '<div class="file-list">';
            
            files.forEach(file => {
                const isLatest = file === latestFile;
                const badge = isLatest ? ' (Latest)' : '';
                const style = isLatest ? 'border-left-color: #28a745;' : '';
                
                html += `
                    <div class="file-item" style="${style}">
                        <div class="file-name">📄 ${file}${badge}</div>
                        <div class="file-details">
                            Threat Intelligence CSV<br>
                            ${isLatest ? '<strong>Most recent data</strong>' : 'Historical data'}
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
            document.getElementById('files-content').innerHTML = html;
        }
        
        function showSampleData(sampleData, columns) {
            if (!sampleData || sampleData.length === 0) {
                document.getElementById('sample-content').innerHTML = 
                    '<div class="status warning">⚠️ No sample data available</div>';
                return;
            }
            
            // Create table with limited columns for better display
            const displayColumns = columns.slice(0, 6); // Show first 6 columns
            let html = `<div class="status success">✅ Showing sample data (first 5 records, ${displayColumns.length} columns)</div>`;
            html += '<table><thead><tr>';
            
            displayColumns.forEach(col => {
                html += `<th>${col}</th>`;
            });
            
            html += '</tr></thead><tbody>';
            
            sampleData.slice(0, 5).forEach(row => {
                html += '<tr>';
                displayColumns.forEach(col => {
                    const value = row[col] || 'N/A';
                    const displayValue = value.length > 50 ? value.substring(0, 47) + '...' : value;
                    html += `<td title="${value}">${displayValue}</td>`;
                });
                html += '</tr>';
            });
            
            html += '</tbody></table>';
            
            if (columns.length > 6) {
                html += `<p style="margin-top: 10px; color: #666; font-size: 0.9em;">
                    <em>Showing ${displayColumns.length} of ${columns.length} columns. Full data available after pipeline execution.</em>
                </p>`;
            }
            
            document.getElementById('sample-content').innerHTML = html;
        }
        
        // Load data on page load
        loadData();
        
        // Auto-refresh every 30 seconds
        setInterval(loadData, 30000);
    </script>
</body>
</html>
        """

def start_server(port=8501):
    """Start the local dashboard server"""
    print("🛡️ Local Threat Intelligence Dashboard")
    print("=" * 50)
    print(f"🚀 Starting server on port {port}")
    print(f"🌐 Dashboard URL: http://localhost:{port}")
    print("📁 Reading from: /opt/airflow/data/")
    print("🔧 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Change to correct directory
    os.chdir('/opt/airflow')
    
    # Start server
    handler = LocalDashboardHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        try:
            print("✅ Server started successfully!")
            print("📊 Dashboard is ready for use...")
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped by user")

if __name__ == "__main__":
    start_server()
