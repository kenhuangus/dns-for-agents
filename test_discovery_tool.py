"""
test_discovery_tool.py
Automated tests for Agent DNS Discovery Tool with real certificate validation.

Assumes:
- ca.pem and agent.pem exist in the current directory.
- discovery_tool.py is present and imports as a module.
- cryptography and jsonschema are installed.
"""
import json
import os
import sys
from discovery_tool import AgentDiscoveryTool, AGENT_CAPABILITY_REQUEST_SCHEMA, AGENT_CAPABILITY_RESPONSE_SCHEMA

def load_agent_cert():
    with open("agent.pem") as f:
        return f.read()

def test_advertisement_and_discovery():
    tool = AgentDiscoveryTool(AGENT_CAPABILITY_REQUEST_SCHEMA, AGENT_CAPABILITY_RESPONSE_SCHEMA, ca_cert_path="ca.pem")
    agent_registry = {}
    available_agents = []

    # Advertisement
    agent_cert_pem = load_agent_cert()
    adv_payload = {
        "requestType": "advertisement",
        "requestingAgent": {
            "protocol": "a2a",
            "agentName": "TranslatorB",
            "agentCategory": "translator",
            "providerName": "openai",
            "version": "1.0",
            # "extension": "agent",  # Optional
            "agentUseJustification": "Provides Legal Translation",
            "agentCapability": "DocumentTranslation",
            "agentEndpoint": "https://translatorb.example.com",
            "agentDID": "did:example:translatorb",
            "certificate": {
                "certificateSubject": "CN=TranslatorB,OU=Agents,O=MyOrg,L=City,S=State,C=US",
                "certificateIssuer": "CN=Test Root CA,OU=TestCA,O=TestOrg,L=TestCity,C=US",
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
    assert adv_response["status"] == "success", f"Advertisement failed: {adv_response['errorMessage']}"

    # Discovery
    available_agents.append(agent_registry[adv_payload["requestingAgent"]["agentDID"]])
    request_payload = {
        "requestType": "discovery",
        "requestingAgent": {
            "protocol": "a2a",
            "agentName": "DocProcA",
            "agentCategory": "document_processor",
            "providerName": "openai",
            "version": "1.0",
            # "extension": "agent",  # Optional
            "agentUseJustification": "Needs translation",
            "agentCapability": "DocumentTranslation",
            "agentEndpoint": "https://docproca.example.com",
            "agentDID": "did:example:docproca",
            "certificate": {
                "certificateSubject": "CN=DocProcA,OU=Agents,O=MyOrg,L=City,S=State,C=US",
                "certificateIssuer": "CN=Test Root CA,OU=TestCA,O=TestOrg,L=TestCity,C=US",
                "certificateSerialNumber": "12345",
                "certificateValidFrom": "2025-01-01T00:00:00Z",
                "certificateValidTo": "2026-01-01T00:00:00Z",
                "certificatePEM": agent_cert_pem,  # For demo, reuse the same cert
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
    assert response["status"] == "success", f"Discovery failed: {response['errorMessage']}"

if __name__ == "__main__":
    test_advertisement_and_discovery()
