import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from jsonschema import validate, ValidationError
from agent_registration_db import deactivate_agent

SCHEMA_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(SCHEMA_DIR, 'agent_deactivation_request_schema.json'), 'r') as f:
    DEACTIVATION_REQUEST_SCHEMA = json.load(f)
with open(os.path.join(SCHEMA_DIR, 'agent_deactivation_response_schema.json'), 'r') as f:
    DEACTIVATION_RESPONSE_SCHEMA = json.load(f)

def validate_json_schema(data, schema):
    try:
        validate(instance=data, schema=schema)
        return True, ''
    except ValidationError as e:
        return False, str(e)

def make_deactivation_response(agentName, success=True, error_message=None):
    if success:
        return {
            "status": "success",
            "deactivatedAgent": agentName
        }
    else:
        return {
            "status": "failure",
            "errorMessage": error_message or "Invalid deactivation request."
        }

class DeactivationHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != '/deactivate':
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
            return
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        try:
            request_json = json.loads(body)
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Invalid JSON')
            return
        valid, error = validate_json_schema(request_json, DEACTIVATION_REQUEST_SCHEMA)
        if not valid:
            response = make_deactivation_response(None, success=False, error_message=error)
            self.send_response(400)
        else:
            # Updated: Extract agent identifier fields according to the new schema structure
            agent_name = request_json.get("agentName")
            protocol = request_json.get("protocol")
            agent_category = request_json.get("agentCategory")
            provider_name = request_json.get("providerName")
            version = request_json.get("version")
            extension = request_json.get("extension")  # Optional
            try:
                found = deactivate_agent(agent_name)
                if not found:
                    response = make_deactivation_response(agent_name, success=False, error_message="Agent not found.")
                    self.send_response(404)
                else:
                    response = make_deactivation_response(agent_name, success=True)
                    self.send_response(200)
            except Exception as e:
                response = make_deactivation_response(agent_name, success=False, error_message=str(e))
                self.send_response(500)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=DeactivationHandler, port=8082):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting deactivation server on port {port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
