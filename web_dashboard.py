#!/usr/bin/env python3
"""
Simplified dashboard that shows threat intel data as a web page
Uses only built-in Python libraries
"""
import http.server
import socketserver
import json
import os
import csv
from datetime import datetime
import webbrowser
import threading

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
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
            
            data = self.get_data()
            self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))
        else:
            self.send_error(404)
    
    def get_data(self):
        """Get threat intelligence data from local files"""
        data_dir = "data"
        result = {
            "timestamp": datetime.now().isoformat(),
            "files": [],
            "summary": {
                "total_files": 0,
                "total_records": 0,
                "latest_file": None
            },
            "sample_data": []
        }
        
        try:
            if os.path.exists(data_dir):
                csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
                result["files"] = csv_files
                result["summary"]["total_files"] = len(csv_files)
                
                if csv_files:
                    # Get latest file
                    latest_file = max(csv_files, key=lambda f: os.path.getmtime(os.path.join(data_dir, f)))
                    result["summary"]["latest_file"] = latest_file
                    
                    # Read sample data
                    try:
                        with open(os.path.join(data_dir, latest_file), 'r', encoding='utf-8') as f:
                            reader = csv.DictReader(f)
                            rows = list(reader)
                            result["summary"]["total_records"] = len(rows)
                            result["sample_data"] = rows[:10]  # First 10 rows
                    except Exception as e:
                        result["error"] = f"Error reading {latest_file}: {str(e)}"
            else:
                result["error"] = f"Data directory '{data_dir}' not found"
                
        except Exception as e:
            result["error"] = f"Error accessing data: {str(e)}"
        
        return result
    
    def create_dashboard_html(self):
        """Create the dashboard HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🛡️ Threat Intelligence Dashboard</title>
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
            font-size: 0.8em; 
            font-weight: bold;
            display: inline-block;
        }
        .status.success { background: #d4edda; color: #155724; }
        .status.error { background: #f8d7da; color: #721c24; }
        .status.warning { background: #fff3cd; color: #856404; }
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
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .file-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        .file-name { font-weight: bold; margin-bottom: 5px; }
        .file-size { color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ Threat Intelligence Dashboard</h1>
            <p>Real-time monitoring of cybersecurity threats and indicators</p>
            <p><small>Last updated: <span id="last-update">Loading...</span></small></p>
        </div>
        
        <button class="refresh-btn" onclick="loadData()">🔄 Refresh Data</button>
        
        <div class="metrics">
            <div class="metric">
                <div class="metric-value" id="total-files">-</div>
                <div class="metric-label">Data Files</div>
            </div>
            <div class="metric">
                <div class="metric-value" id="total-records">-</div>
                <div class="metric-label">Total Records</div>
            </div>
            <div class="metric">
                <div class="metric-value" id="latest-file-short">-</div>
                <div class="metric-label">Latest Dataset</div>
            </div>
            <div class="metric">
                <div class="metric-value" id="status-indicator">🔄</div>
                <div class="metric-label">System Status</div>
            </div>
        </div>
        
        <div class="card">
            <h3>📊 Data Files Overview</h3>
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
            
            if (data.summary.latest_file) {
                // Show shortened filename
                const shortName = data.summary.latest_file.length > 20 
                    ? '...' + data.summary.latest_file.slice(-17) 
                    : data.summary.latest_file;
                document.getElementById('latest-file-short').textContent = shortName;
            } else {
                document.getElementById('latest-file-short').textContent = 'None';
            }
            
            // Update status
            if (data.error) {
                document.getElementById('status-indicator').textContent = '❌';
                showError(data.error);
            } else if (data.files.length === 0) {
                document.getElementById('status-indicator').textContent = '⚠️';
                showWarning('No data files found. Run your Airflow pipeline to generate data.');
            } else {
                document.getElementById('status-indicator').textContent = '✅';
                showFiles(data.files);
                showSampleData(data.sample_data);
            }
        }
        
        function showError(message) {
            document.getElementById('files-content').innerHTML = 
                `<div class="status error">❌ Error: ${message}</div>`;
            document.getElementById('sample-content').innerHTML = 
                `<div class="status error">❌ No sample data available due to error</div>`;
        }
        
        function showWarning(message) {
            document.getElementById('files-content').innerHTML = 
                `<div class="status warning">⚠️ ${message}</div>`;
            document.getElementById('sample-content').innerHTML = 
                `<div class="status warning">⚠️ No sample data available</div>`;
        }
        
        function showFiles(files) {
            if (files.length === 0) {
                document.getElementById('files-content').innerHTML = 
                    '<div class="status warning">⚠️ No CSV files found</div>';
                return;
            }
            
            let html = `<div class="status success">✅ Found ${files.length} data files</div>`;
            html += '<div class="file-list">';
            
            files.forEach(file => {
                html += `
                    <div class="file-item">
                        <div class="file-name">📄 ${file}</div>
                        <div class="file-size">CSV Data File</div>
                    </div>
                `;
            });
            
            html += '</div>';
            document.getElementById('files-content').innerHTML = html;
        }
        
        function showSampleData(sampleData) {
            if (!sampleData || sampleData.length === 0) {
                document.getElementById('sample-content').innerHTML = 
                    '<div class="status warning">⚠️ No sample data available</div>';
                return;
            }
            
            // Create table
            const columns = Object.keys(sampleData[0]);
            let html = '<div class="status success">✅ Showing first 10 records</div>';
            html += '<table><thead><tr>';
            
            columns.slice(0, 6).forEach(col => {  // Show first 6 columns
                html += `<th>${col}</th>`;
            });
            
            html += '</tr></thead><tbody>';
            
            sampleData.slice(0, 5).forEach(row => {  // Show first 5 rows
                html += '<tr>';
                columns.slice(0, 6).forEach(col => {
                    const value = row[col] || 'N/A';
                    const displayValue = value.length > 50 ? value.substring(0, 47) + '...' : value;
                    html += `<td>${displayValue}</td>`;
                });
                html += '</tr>';
            });
            
            html += '</tbody></table>';
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

def start_server(port=8502):
    """Start the dashboard server"""
    print("🛡️ Threat Intelligence Dashboard")
    print("=" * 40)
    print(f"🚀 Starting server on port {port}")
    print(f"🌐 Dashboard URL: http://localhost:{port}")
    print("🔧 Press Ctrl+C to stop the server")
    print("=" * 40)
    
    # Change to script directory so relative paths work
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Start server
    handler = DashboardHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        try:
            # Open browser automatically
            threading.Timer(1.5, lambda: webbrowser.open(f'http://localhost:{port}')).start()
            print("✅ Server started successfully!")
            print("📊 Dashboard should open in your browser...")
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped by user")

if __name__ == "__main__":
    start_server()
