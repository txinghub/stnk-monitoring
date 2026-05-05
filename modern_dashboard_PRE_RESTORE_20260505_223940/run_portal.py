#!/usr/bin/env python3
"""Run portal on 8888"""
import http.server
import socketserver

PORT = 8080
DIRECTORY = "/Users/linggothioputro/stnk-monitoring/modern_dashboard"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    def do_GET(self):
        if self.path == "/":
            self.path = "/portal.html"
        return super().do_GET()

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Portal on {PORT}")
    httpd.serve_forever()
