import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from urllib.parse import urlparse, parse_qs
from agent_registration_db import get_agent_status

class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != '/status':
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
            return
        params = parse_qs(parsed.query)
        # Updated: Extract agent identifier fields according to the new schema structure
        agent_name = params.get('agentName', [None])[0]
        protocol = params.get('protocol', [None])[0]
        agent_category = params.get('agentCategory', [None])[0]
        provider_name = params.get('providerName', [None])[0]
        version = params.get('version', [None])[0]
        extension = params.get('extension', [None])[0]
        if not agent_name:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Missing agentName parameter')
            return
        try:
            status = get_agent_status(agent_name)
            if status is None:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(json.dumps({"status": "not found", "agentName": agent_name}).encode('utf-8'))
            else:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": status, "agentName": agent_name}).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=StatusHandler, port=8083):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting status server on port {port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
