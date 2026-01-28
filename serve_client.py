#!/usr/bin/env python3
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
    
    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format%args}")

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("="*60)
print("Web Client Server Starting...")
print(f"Serving on: http://0.0.0.0:8080")
print(f"Open in browser: http://YOUR_EC2_IP:8080")
print("="*60)

server = HTTPServer(('0.0.0.0', 8080), CORSRequestHandler)
server.serve_forever()
