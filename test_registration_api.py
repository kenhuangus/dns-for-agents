import requests
import json

def test_registration():
    url = 'http://localhost:8080/register'
    headers = {'Content-Type': 'application/json'}

    # 1. Valid registration
    registration = {
        "requestType": "registration",
        "requestingAgent": {
            "agentName": "TestAgent",
            "agentPolicyId": "policy1",
            "agentUseJustification": "Testing registration",
            "agentCapability": "DocumentTranslation",
            "agentEndpoint": "http://localhost:9000/agent",
            "agentDID": "did:example:123456789abcdefghi",
            "certificate": {
                "certificateSubject": "CN=TestAgent,O=TestOrg,C=US",
                "certificateIssuer": "CN=LocalCA,O=TestOrg,C=US",
                "certificateSerialNumber": "1234567890",
                "certificateValidFrom": "2025-04-20T00:00:00Z",
                "certificateValidTo": "2026-04-20T00:00:00Z",
                "certificatePEM": "-----BEGIN CERTIFICATE-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAn...\n-----END CERTIFICATE-----",
                "certificatePublicKeyAlgorithm": "RSA",
                "certificateSignatureAlgorithm": "SHA256withRSA"
            },
            "csrPEM": "BASE64PEMSTRING==",
            "a2aAgentCard": {
                "agentName": "TestAgent",
                "description": "A test agent card",
                "capabilities": ["DocumentTranslation"],
                "endpoints": [
                    {"protocol": "http", "url": "http://localhost:9000/agent"}
                ]
            },
            "mcpClientInformation": {
                "supportedTools": ["tool1", "tool2"],
                "supportedResources": ["resource1"]
            },
            "agentDNSName": "testagent.agentic.ai"
        }
    }
    print('\n--- Valid Registration ---')
    response = requests.post(url, data=json.dumps(registration), headers=headers)
    print('Status Code:', response.status_code)
    print('Response:', response.json())

    # 2. Missing required field (agentName)
    invalid_registration = json.loads(json.dumps(registration))
    del invalid_registration["requestingAgent"]["agentName"]
    print('\n--- Missing agentName ---')
    response = requests.post(url, data=json.dumps(invalid_registration), headers=headers)
    print('Status Code:', response.status_code)
    print('Response:', response.json())

    # 3. Invalid field type (agentCapability as int)
    invalid_type_registration = json.loads(json.dumps(registration))
    invalid_type_registration["requestingAgent"]["agentCapability"] = 123
    print('\n--- Invalid agentCapability type ---')
    response = requests.post(url, data=json.dumps(invalid_type_registration), headers=headers)
    print('Status Code:', response.status_code)
    print('Response:', response.json())

    # 4. Duplicate registration (same agentName)
    print('\n--- Duplicate Registration ---')
    response = requests.post(url, data=json.dumps(registration), headers=headers)
    print('Status Code:', response.status_code)
    print('Response:', response.json())

    # 5. Invalid certificate (not signed by CA)
    invalid_cert_registration = json.loads(json.dumps(registration))
    invalid_cert_registration["requestingAgent"]["certificate"]["certificatePEM"] = """-----BEGIN CERTIFICATE-----\nMIIBsjCCAVugAwIBAgIUQ1RANDOMINVALID1234567890wDQYJKoZIhvcNAQELBQAwEjEQMA4GA1UEAwwHUmFuZG9tQ0EwHhcNMjUwNDE5MDAwMDAwWhcNMjYwNDE5MDAwMDAwWjASMRAwDgYDVQQDDAdSYW5kb21DQTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALo1w7zF1Q5+Qw4fK0F5RZBq9XwFZ2bT+3e3QwIDAQABo1MwUTAdBgNVHQ4EFgQU6QjvRANDOMINVALID1234567890wHwYDVR0jBBgwFoAU6QjvRANDOMINVALID1234567890wDwYDVR0TAQH/BAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAQEADummySignature==\n-----END CERTIFICATE-----"""
    print('\n--- Invalid Certificate (not signed by CA) ---')
    response = requests.post(url, data=json.dumps(invalid_cert_registration), headers=headers)
    print('Status Code:', response.status_code)
    try:
        print('Response:', response.json())
    except Exception as e:
        print('Response could not be parsed:', e)

    # 6. Completely invalid JSON
    print('\n--- Invalid JSON ---')
    response = requests.post(url, data='{bad json}', headers=headers)
    print('Status Code:', response.status_code)
    try:
        print('Response:', response.json())
    except Exception as e:
        print('Response could not be parsed:', e)

import sqlite3
import os

if __name__ == "__main__":
    test_registration()
    # Show all rows in the database with column names
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agent_registration.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('PRAGMA table_info(agent_registrations)')
    columns = [desc[1] for desc in c.fetchall()]
    c.execute('SELECT * FROM agent_registrations')
    rows = c.fetchall()
    print('\nDatabase contents:')
    print(', '.join(columns))
    for row in rows:
        for col, val in zip(columns, row):
            print(f"{col}: {val}")
        print('-' * 40)
    conn.close()
