#!/usr/bin/env python3
"""Custom Portal Server - serves portal.html at root"""
import http.server
import socketserver
import os

PORT = 8888
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class PortalHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.path = '/portal.html'
        return super().do_GET()

with socketserver.TCPServer(("", PORT), PortalHandler) as httpd:
    print(f"Portal server running at http://localhost:{PORT}")
    httpd.serve_forever()
