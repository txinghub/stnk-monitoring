#!/usr/bin/env python3
"""Simple HTTP server for STNK dashboard on port 8099"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8099
DATA_FILE = "data.json"

class SimpleDashboardHandler(BaseHTTPRequestHandler):
    """Simple HTTP request handler for dashboard"""
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            path = self.path
            
            # API endpoint for data
            if path == '/api/data':
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                # Read and send data.json
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
    
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, SimpleDashboardHandler)
    
    print(f"Server started at http://localhost:{PORT}")
    print("Press Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")

if __name__ == '__main__':
    main()