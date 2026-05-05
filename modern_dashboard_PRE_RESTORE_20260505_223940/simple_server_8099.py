#!/usr/bin/env python3
"""Simple HTTP server for STNK dashboard on port 8099 - with auto date recalculation"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, date

PORT = 8099
DATA_FILE = "data.json"

def get_status(days):
    """Determine status based on days remaining"""
    if days is None or days == 9999:
        return "unknown"
    if days <= 0:
        return "expired"
    if days <= 7:
        return "priority"
    if days <= 30:
        return "warning"
    return "safe"

def recalculate_days(data):
    """Recalculate days remaining for each vehicle based on today's date"""
    today = date.today()
    for item in data:
        stnk_str = item.get('STNK', '') or ''
        pajak_str = item.get('PAJAK', '') or ''
        
        stnk_days = 9999
        pajak_days = 9999
        
        if stnk_str:
            try:
                stnk_date = datetime.strptime(stnk_str, '%Y-%m-%d').date()
                stnk_days = (stnk_date - today).days
            except:
                stnk_days = 9999
        
        if pajak_str:
            try:
                pajak_date = datetime.strptime(pajak_str, '%Y-%m-%d').date()
                pajak_days = (pajak_date - today).days
            except:
                pajak_days = 9999
        
        item['stnk_days'] = stnk_days
        item['pajak_days'] = pajak_days
        item['days_to_expiry'] = min(stnk_days, pajak_days)
        item['HARI_TERSISA'] = min(stnk_days, pajak_days)
        item['status'] = get_status(item['days_to_expiry'])
    
    return data

class SimpleDashboardHandler(BaseHTTPRequestHandler):
    """Simple HTTP request handler for dashboard"""
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            path = self.path
            
            # API endpoint for data - with auto recalculation
            if path == '/api/data':
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                # Read and recalculate days
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                data = recalculate_days(data)
                self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
                
            # Serve index.html
            elif path == '/' or path == '/index.html':
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                
                with open('index.html', 'r', encoding='utf-8') as f:
                    html = f.read()
                self.wfile.write(html.encode('utf-8'))
                
            # Serve other static files
            else:
                # Try to serve file
                file_path = path[1:]  # Remove leading slash
                if os.path.exists(file_path):
                    self.send_response(200)
                    
                    # Set content type
                    if file_path.endswith('.js'):
                        self.send_header('Content-Type', 'application/javascript')
                    elif file_path.endswith('.css'):
                        self.send_header('Content-Type', 'text/css')
                    elif file_path.endswith('.json'):
                        self.send_header('Content-Type', 'application/json')
                    else:
                        self.send_header('Content-Type', 'text/plain')
                    
                    self.end_headers()
                    
                    with open(file_path, 'rb') as f:
                        self.wfile.write(f.read())
                else:
                    self.send_error(404, "File not found")
                    
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")
    
    def log_message(self, format, *args):
        """Override to reduce log noise"""
        pass

def main():
    """Start the HTTP server"""
    print(f"Starting STNK Dashboard server on port {PORT}...")
    print(f"Serving from: {os.getcwd()}")
    print(f"Data file: {DATA_FILE}")
    
    # Listen on localhost (Tailscale Serve handles external access)
    server_address = ('127.0.0.1', PORT)
    httpd = HTTPServer(server_address, SimpleDashboardHandler)
    httpd.allow_reuse_address = True
    
    print(f"Server started at http://localhost:{PORT}")
    print("Press Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")

if __name__ == '__main__':
    main()
