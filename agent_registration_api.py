import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from jsonschema import validate, ValidationError
from agent_registration_db import insert_registration
import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import base64

# Load JSON Schemas
SCHEMA_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(SCHEMA_DIR, 'agent_registration_request_schema.json'), 'r') as f:
    REGISTRATION_REQUEST_SCHEMA = json.load(f)
with open(os.path.join(SCHEMA_DIR, 'agent_registration_response_schema.json'), 'r') as f:
    REGISTRATION_RESPONSE_SCHEMA = json.load(f)

def validate_json_schema(data, schema):
    try:
        validate(instance=data, schema=schema)
        return True, ''
    except ValidationError as e:
        return False, str(e)

def make_registration_response(request_data, success=True, error_message=None):
    if success:
        response = {
            "status": "success",
            "respondingAgent": request_data["requestingAgent"]
        }
        # Add required fields for response schema compliance
        # Updated: Populate new agent identifier fields according to the new schema structure
        response["respondingAgent"].update({
            "protocol": request_data["requestingAgent"].get("protocol", "a2a"),
            "agentName": request_data["requestingAgent"].get("agentName", ""),
            "agentCategory": request_data["requestingAgent"].get("agentCategory", ""),
            "providerName": request_data["requestingAgent"].get("providerName", ""),
            "version": request_data["requestingAgent"].get("version", "1.0"),
            "extension": request_data["requestingAgent"].get("extension", ""),
            "certificate": {},
            "registrationTimestamp": "2025-04-20T11:03:00Z",
            "renewalTimestamp": "2025-04-20T11:03:00Z",
            "agentStatus": "active"
        })
        # Dummy mcpServerInformation
        response["respondingAgent"]["mcpServerInformation"] = {"tools": [], "resources": []}
        # Add missing required fields if not present
        for k in ["agentCapability", "agentEndpoint", "agentDID", "a2aAgentCard", "agentDNSName", "agentUseJustification"]:
            if k not in response["respondingAgent"]:
                response["respondingAgent"][k] = ""
        return response
    else:
        return {
            "status": "failure",
            "errorMessage": error_message or "Invalid registration request.",
            "respondingAgent": {}
        }

class RegistrationHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != '/register':
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
        valid, error = validate_json_schema(request_json, REGISTRATION_REQUEST_SCHEMA)
        if not valid:
            response = make_registration_response(request_json, success=False, error_message=error)
            self.send_response(400)
        else:
            # Validate certificate against local CA
            try:
                cert_pem = request_json["requestingAgent"]["certificate"]["certificatePEM"].encode()
                cert = x509.load_pem_x509_certificate(cert_pem, default_backend())
                with open(os.path.join(SCHEMA_DIR, "ca.pem"), "rb") as f:
                    ca_cert = x509.load_pem_x509_certificate(f.read(), default_backend())
                # Check that issuer matches CA
                if cert.issuer != ca_cert.subject:
                    raise ValueError("Certificate not issued by local CA")
                # Verify signature
                ca_public_key = ca_cert.public_key()
                ca_public_key.verify(
                    cert.signature,
                    cert.tbs_certificate_bytes,
                    padding.PKCS1v15(),
                    cert.signature_hash_algorithm,
                )
            except Exception as e:
                response = make_registration_response(request_json, success=False, error_message=f"Certificate validation failed: {e}")
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
            # Add registration timestamp
            now = datetime.datetime.utcnow().isoformat() + 'Z'
            request_json["requestingAgent"]["registrationTimestamp"] = now
            # Insert into database
            insert_registration(request_json["requestingAgent"])
            response = make_registration_response(request_json, success=True)
            self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=RegistrationHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting registration server on port {port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
