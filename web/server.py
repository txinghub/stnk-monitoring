#!/usr/bin/env python3
"""Simple HTTP server for STNK dashboard on port 8099"""

import json
import os
from datetime import datetime, date
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8099
DATA_FILE = "data.json"

class SimpleDashboardHandler(BaseHTTPRequestHandler):
    """Simple HTTP request handler for dashboard"""
    
    def calculate_days(self, date_str):
        """Calculate days from today to given date"""
        if not date_str:
            return 9999  # Far future if no date
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            return (target_date - date.today()).days  # Can be negative
        except ValueError:
            return 9999
    
    def calculate_status(self, days):
        """Calculate status based on days to expiry"""
        if days <= 0:
            return 'expired'
        elif days <= 30:
            return 'priority'
        elif days <= 90:
            return 'warning'
        else:
            return 'safe'
    
    def enrich_data(self, data):
        """Enrich raw data with real-time calculated days"""
        enriched = []
        for vehicle in data:
            stnk_days = self.calculate_days(vehicle.get('STNK', ''))
            pajak_days = self.calculate_days(vehicle.get('PAJAK', ''))
            days_to_expiry = min(stnk_days, pajak_days)
            
            enriched.append({
                **vehicle,
                'stnk_days': stnk_days,
                'pajak_days': pajak_days,
                'days_to_expiry': days_to_expiry,
                'status': self.calculate_status(days_to_expiry)
            })
        return enriched
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            path = self.path
            
            # API endpoint for real-time enriched data
            if path == '/api/enriched':
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                enriched = self.enrich_data(data)
                self.wfile.write(json.dumps(enriched, ensure_ascii=False, indent=2).encode('utf-8'))
            
            # API endpoint for raw data (backwards compat)
            elif path == '/api/data':
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = f.read()
                self.wfile.write(data.encode('utf-8'))
                
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
    
    server_address = ('127.0.0.1', PORT)
    httpd = HTTPServer(server_address, SimpleDashboardHandler)
    
    print(f"Server started at http://localhost:{PORT}")
    print("Press Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")

if __name__ == '__main__':
    main()