"""
Simplified Threat Intelligence Dashboard
Runs directly in Airflow environment without additional dependencies
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
from datetime import datetime

class ThreatIntelHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html_content = self.generate_dashboard_html()
            self.wfile.write(html_content.encode())
        
        elif self.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Get data from your local files
            data = self.get_threat_data()
            self.wfile.write(json.dumps(data).encode())
        
        else:
            super().do_GET()
    
    def get_threat_data(self):
        """Get threat data from local CSV files"""
        data_dir = "/opt/airflow/data"
        data = {
            "files": [],
            "summary": {"total_files": 0, "latest_file": None}
        }
        
        try:
            if os.path.exists(data_dir):
                files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
                data["files"] = files
                data["summary"]["total_files"] = len(files)
                
                if files:
                    # Get latest file
                    latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(data_dir, f)))
                    data["summary"]["latest_file"] = latest_file
                    
                    # Read sample data from latest file
                    try:
                        import pandas as pd
                        df = pd.read_csv(os.path.join(data_dir, latest_file))
                        data["sample_data"] = {
                            "rows": len(df),
                            "columns": list(df.columns),
                            "head": df.head(5).to_dict('records')
                        }
                    except:
                        data["sample_data"] = {"error": "Could not read CSV file"}
        except Exception as e:
            data["error"] = str(e)
        
        return data
    
    def generate_dashboard_html(self):
        """Generate simple HTML dashboard"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>🛡️ Threat Intelligence Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header { 
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white; 
            padding: 30px; 
            text-align: center; 
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.1em; opacity: 0.9; }
        .content { padding: 30px; }
        .card { 
            background: #f8f9fa; 
            border-radius: 10px; 
            padding: 20px; 
            margin-bottom: 20px;
            border-left: 4px solid #4facfe;
        }
        .metrics { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px;
        }
        .metric {
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.07);
            border-top: 3px solid #4facfe;
        }
        .metric-value { font-size: 2em; font-weight: bold; color: #4facfe; }
        .metric-label { color: #666; margin-top: 5px; }
        .loading { text-align: center; padding: 50px; color: #666; }
        .error { color: #e74c3c; background: #ffeaea; padding: 15px; border-radius: 5px; }
        .success { color: #27ae60; background: #eafaf1; padding: 15px; border-radius: 5px; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; font-weight: 600; }
        .refresh-btn {
            background: #4facfe;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin-bottom: 20px;
        }
        .refresh-btn:hover { background: #3d8bfe; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ Threat Intelligence Dashboard</h1>
            <p>Real-time threat data analysis and monitoring</p>
        </div>
        
        <div class="content">
            <button class="refresh-btn" onclick="loadData()">🔄 Refresh Data</button>
            
            <div class="metrics" id="metrics">
                <div class="metric">
                    <div class="metric-value" id="total-files">-</div>
                    <div class="metric-label">Data Files</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="total-rows">-</div>
                    <div class="metric-label">Total Records</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="latest-file">-</div>
                    <div class="metric-label">Latest File</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="last-updated">-</div>
                    <div class="metric-label">Last Updated</div>
                </div>
            </div>
            
            <div class="card">
                <h3>📊 Data Overview</h3>
                <div id="data-content">
                    <div class="loading">Loading threat intelligence data...</div>
                </div>
            </div>
            
            <div class="card">
                <h3>📋 Sample Data</h3>
                <div id="sample-table">
                    <div class="loading">Loading sample records...</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function loadData() {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    updateDashboard(data);
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('data-content').innerHTML = 
                        '<div class="error">❌ Error loading data: ' + error.message + '</div>';
                });
        }
        
        function updateDashboard(data) {
            // Update metrics
            document.getElementById('total-files').textContent = data.summary.total_files || 0;
            document.getElementById('latest-file').textContent = data.summary.latest_file || 'None';
            document.getElementById('last-updated').textContent = new Date().toLocaleTimeString();
            
            if (data.sample_data && data.sample_data.rows) {
                document.getElementById('total-rows').textContent = data.sample_data.rows;
            } else {
                document.getElementById('total-rows').textContent = 'N/A';
            }
            
            // Update data content
            if (data.error) {
                document.getElementById('data-content').innerHTML = 
                    '<div class="error">❌ Error: ' + data.error + '</div>';
            } else if (data.files.length === 0) {
                document.getElementById('data-content').innerHTML = 
                    '<div class="error">⚠️ No CSV files found. Please run your Airflow pipeline first.</div>';
            } else {
                let html = '<div class="success">✅ Found ' + data.files.length + ' data files:</div><ul>';
                data.files.forEach(file => {
                    html += '<li>' + file + '</li>';
                });
                html += '</ul>';
                document.getElementById('data-content').innerHTML = html;
            }
            
            // Update sample table
            if (data.sample_data && data.sample_data.head) {
                let table = '<table><thead><tr>';
                data.sample_data.columns.forEach(col => {
                    table += '<th>' + col + '</th>';
                });
                table += '</tr></thead><tbody>';
                
                data.sample_data.head.forEach(row => {
                    table += '<tr>';
                    data.sample_data.columns.forEach(col => {
                        table += '<td>' + (row[col] || 'N/A') + '</td>';
                    });
                    table += '</tr>';
                });
                table += '</tbody></table>';
                document.getElementById('sample-table').innerHTML = table;
            } else {
                document.getElementById('sample-table').innerHTML = 
                    '<div class="loading">No sample data available</div>';
            }
        }
        
        // Load data on page load
        loadData();
        
        // Auto-refresh every 30 seconds
        setInterval(loadData, 30000);
    </script>
</body>
</html>
        """

def start_dashboard(port=8501):
    """Start the simple dashboard server"""
    print(f"🚀 Starting Threat Intelligence Dashboard on port {port}")
    print(f"🌐 Access at: http://localhost:{port}")
    print("🔧 Press Ctrl+C to stop")
    print("=" * 50)
    
    server = HTTPServer(('0.0.0.0', port), ThreatIntelHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
        server.shutdown()

if __name__ == "__main__":
    start_dashboard()
