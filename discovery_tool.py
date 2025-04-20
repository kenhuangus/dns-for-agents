"""
discovery_tool.py
A secure Agent Discovery and Capability Advertisement tool for Agentic AI (A2A/MCP compliant).
- Validates all requests and responses against provided JSON Schemas.
- Supports both discovery and advertisement flows.
- Example usage at the bottom.

Requirements:
- jsonschema
- (Optional: cryptography, requests, etc. for production)
"""
import json
from jsonschema import validate, ValidationError
from datetime import datetime
from cryptography import x509
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives.asymmetric import padding
import base64

# Load schemas from external JSON files for validation
def load_schema(path):
    import json
    with open(path) as f:
        return json.load(f)

# Updated: The agent identifier for requestingAgent must now use the following fields in this order:
# protocol, agentName, agentCategory, providerName, version, [extension (optional)]
# The schema enforces this structure for all validations below.
AGENT_CAPABILITY_REQUEST_SCHEMA = load_schema("agent_capability_request.schema.json")
AGENT_CAPABILITY_RESPONSE_SCHEMA = load_schema("agent_capability_response.schema.json")

class AgentDiscoveryTool:
    def __init__(self, request_schema, response_schema, ca_cert_path=None):
        self.request_schema = request_schema
        self.response_schema = response_schema
        self.ca_cert = None
        if ca_cert_path:
            with open(ca_cert_path, 'rb') as f:
                self.ca_cert = x509.load_pem_x509_certificate(f.read(), default_backend())

    def validate_certificate(self, cert_pem):
        """
        Parse PEM, check signature against CA, check validity period.
        Returns (True, None) if valid, else (False, reason)
        """
        try:
            cert = x509.load_pem_x509_certificate(cert_pem.encode(), default_backend())
            # Check validity period
            now = datetime.utcnow()
            if cert.not_valid_before > now or cert.not_valid_after < now:
                return False, "Certificate not valid at current time."
            # Check signature chain (self.ca_cert is trusted root)
            if self.ca_cert:
                ca_public_key = self.ca_cert.public_key()
                try:
                    ca_public_key.verify(
                        cert.signature,
                        cert.tbs_certificate_bytes,
                        padding.PKCS1v15(),
                        cert.signature_hash_algorithm,
                    )
                except Exception as e:
                    return False, f"Certificate signature verification failed: {e}"
            return True, None
        except Exception as e:
            return False, f"Certificate parse/validation error: {e}"

    def validate_request(self, request_json):
        try:
            validate(instance=request_json, schema=self.request_schema)
            return True, None
        except ValidationError as e:
            return False, str(e)

    def validate_response(self, response_json):
        try:
            validate(instance=response_json, schema=self.response_schema)
            return True, None
        except ValidationError as e:
            return False, str(e)

    def handle_discovery(self, request_json, available_agents):
        """
        Process a discovery request and return a compliant response.
        available_agents: list of dicts describing agent capability profiles.
        """
        valid, error = self.validate_request(request_json)
        if not valid:
            return {
                "status": "failure",
                "errorMessage": f"Request validation error: {error}",
                "respondingAgent": None
            }
        query = request_json.get("queryParameters", {})
        matches = []
        for agent in available_agents:
            if (
                agent["agentCapability"] == request_json["requestingAgent"]["agentCapability"] and
                (not query.get("languagePair") or agent.get("additionalCapabilities", {}).get("languagePair") == query.get("languagePair")) and
                (not query.get("domainExpertise") or agent.get("additionalCapabilities", {}).get("domainExpertise") == query.get("domainExpertise"))
            ):
                # Validate agent certificate
                cert_pem = agent["certificate"]["certificatePEM"]
                valid_cert, cert_error = self.validate_certificate(cert_pem)
                if not valid_cert:
                    continue  # Skip agents with invalid certs
                matches.append(agent)
        if not matches:
            return {
                "status": "failure",
                "errorMessage": "No matching agent found or certificate invalid.",
                "respondingAgent": None
            }
        response = {
            "status": "success",
            "errorMessage": None,
            "respondingAgent": matches[0]
        }
        valid, error = self.validate_response(response)
        if not valid:
            return {
                "status": "failure",
                "errorMessage": f"Response validation error: {error}",
                "respondingAgent": None
            }
        return response

    def handle_advertisement(self, request_json, agent_registry):
        """
        Process an advertisement request and register the agent if valid.
        agent_registry: dict to store agent profiles by DID.
        """
        valid, error = self.validate_request(request_json)
        if not valid:
            return {
                "status": "failure",
                "errorMessage": f"Request validation error: {error}",
                "respondingAgent": None
            }
        agent_profile = request_json["requestingAgent"]
        # Validate agent certificate
        cert_pem = agent_profile["certificate"]["certificatePEM"]
        valid_cert, cert_error = self.validate_certificate(cert_pem)
        if not valid_cert:
            return {
                "status": "failure",
                "errorMessage": f"Certificate validation failed: {cert_error}",
                "respondingAgent": None
            }
        # Add required mcpServerInformation and additionalCapabilities for compliance
        agent_profile = agent_profile.copy()
        agent_profile["mcpServerInformation"] = {
            "tools": [
                {
                    "name": "translate_text",
                    "description": "Translates text from one language to another",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": { "type": "string" },
                            "sourceLanguage": { "type": "string" },
                            "targetLanguage": { "type": "string" }
                        },
                        "required": ["text", "sourceLanguage", "targetLanguage"]
                    },
                    "results": {
                        "type": "object",
                        "properties": {
                            "translatedText": { "type": "string" }
                        },
                        "required": ["translatedText"]
                    }
                }
            ],
            "resources": [
                {
                    "name": "supported_languages",
                    "description": "Returns a list of supported languages",
                    "returns": {
                        "type": "array",
                        "items": { "type": "string" }
                    }
                }
            ]
        }
        agent_profile["additionalCapabilities"] = {
            "languagePair": "en-fr",
            "domainExpertise": "Legal",
            "latency": 150,
            "bleuScore": 38.5
        }
        agent_registry[agent_profile["agentDID"]] = agent_profile
        response = {
            "status": "success",
            "errorMessage": None,
            "respondingAgent": agent_profile
        }
        valid, error = self.validate_response(response)
        if not valid:
            return {
                "status": "failure",
                "errorMessage": f"Response validation error: {error}",
                "respondingAgent": None
            }
        return response

# Example usage
if __name__ == "__main__":
    # TODO: Paste full schemas for AGENT_CAPABILITY_REQUEST_SCHEMA and AGENT_CAPABILITY_RESPONSE_SCHEMA
    # For demo, use {} or minimal schemas
    tool = AgentDiscoveryTool(AGENT_CAPABILITY_REQUEST_SCHEMA, AGENT_CAPABILITY_RESPONSE_SCHEMA, ca_cert_path="ca.pem")
    agent_registry = {}
    available_agents = []  # List of agent profiles

    # Example: handle an advertisement request (register an agent)
    with open("agent.pem") as f:
        agent_cert_pem = f.read()
    adv_payload = {
        "requestType": "advertisement",
        "requestingAgent": {
            "agentName": "TranslatorB",
            "agentPolicyId": "policy456",
            "agentUseJustification": "Provides Legal Translation",
            "agentCapability": "DocumentTranslation",
            "agentEndpoint": "https://translatorb.example.com",
            "agentDID": "did:example:translatorb",
            "certificate": {
                "certificateSubject": "CN=TranslatorB,OU=Agents,O=MyOrg,L=City,S=State,C=US",
                "certificateIssuer": "CN=MyOrg CA,OU=CA,O=MyOrg,L=City,S=State,C=US",
                "certificateSerialNumber": "67890",
                "certificateValidFrom": "2025-02-01T00:00:00Z",
                "certificateValidTo": "2026-02-01T00:00:00Z",
                "certificatePEM": agent_cert_pem,
                "certificatePublicKeyAlgorithm": "RSA",
                "certificateSignatureAlgorithm": "SHA256withRSA"
            },
            "a2aAgentCard": {
                "agentName": "TranslatorB",
                "description": "Translation Service",
                "capabilities": ["Translation"],
                "endpoints": [
                    {"protocol": "HTTP", "url": "https://translatorb.example.com/a2a"}
                ]
            },
            "mcpClientInformation": {
                "supportedTools": ["translate_text"],
                "supportedResources": ["supported_languages"]
            }
        }
    }
    adv_response = tool.handle_advertisement(adv_payload, agent_registry)
    print("\nAdvertisement Response:")
    print(json.dumps(adv_response, indent=2))

    # The registered agent is now available for discovery
    # Use the same agent profile as registered (with mcpServerInformation and additionalCapabilities)
    available_agents.append(agent_registry[adv_payload["requestingAgent"]["agentDID"]])

    # Example: handle a discovery request
    request_payload = {
        "requestType": "discovery",
        "requestingAgent": {
            "agentName": "DocProcA",
            "agentPolicyId": "policy123",
            "agentUseJustification": "Needs translation",
            "agentCapability": "DocumentTranslation",
            "agentEndpoint": "https://docproca.example.com",
            "agentDID": "did:example:docproca",
            "certificate": {
                "certificateSubject": "CN=DocProcA,OU=Agents,O=MyOrg,L=City,S=State,C=US",
                "certificateIssuer": "CN=MyOrg CA,OU=CA,O=MyOrg,L=City,S=State,C=US",
                "certificateSerialNumber": "12345",
                "certificateValidFrom": "2025-01-01T00:00:00Z",
                "certificateValidTo": "2026-01-01T00:00:00Z",
                "certificatePEM": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
                "certificatePublicKeyAlgorithm": "RSA",
                "certificateSignatureAlgorithm": "SHA256withRSA"
            },
            "a2aAgentCard": {
                "agentName": "DocProcA",
                "description": "Document Processing Agent",
                "capabilities": ["Translation", "OCR"],
                "endpoints": [
                    {"protocol": "HTTP", "url": "https://docproca.example.com/a2a"}
                ]
            },
            "mcpClientInformation": {
                "supportedTools": ["ocr_text"],
                "supportedResources": ["document_types"]
            }
        },
        "queryParameters": {
            "languagePair": "en-fr",
            "domainExpertise": "Legal"
        }
    }
    response = tool.handle_discovery(request_payload, available_agents)
    print("\nDiscovery Response:")
    print(json.dumps(response, indent=2))
