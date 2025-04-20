import requests
import json

def test_renewal():
    url = 'http://localhost:8081/renew'
    headers = {'Content-Type': 'application/json'}

    renewal = {
        "requestType": "renewal",
        "requestingAgent": {
            "agentName": "TestAgent",
            "agentDID": "did:example:123456789abcdefghi",
            "certificate": {
                "certificateSubject": "CN=TestAgent,O=TestOrg,C=US",
                "certificateIssuer": "CN=LocalCA,O=TestOrg,C=US",
                "certificateSerialNumber": "1234567890",
                "certificateValidFrom": "2025-04-20T00:00:00Z",
                "certificateValidTo": "2026-04-20T00:00:00Z",
                "certificatePEM": "-----BEGIN CERTIFICATE-----\nMIIDlTCCAn2gAwIBAgIUcxtoEyqDbZInbf77KT4vOmLmKH8wDQYJKoZIhvcNAQEL\nBQAwWjEVMBMGA1UEAwwMVGVzdCBSb290IENBMQ8wDQYDVQQLDAZUZXN0Q0ExEDAO\nBgNVBAoMB1Rlc3RPcmcxETAPBgNVBAcMCFRlc3RDaXR5MQswCQYDVQQGEwJVUzAe\nFw0yNTA0MjAwMDAxMDRaFw0zNTA0MTgwMDAxMDRaMFoxFTATBgNVBAMMDFRlc3Qg\nUm9vdCBDQTEPMA0GA1UECwwGVGVzdENBMRAwDgYDVQQKDAdUZXN0T3JnMREwDwYD\nVQQHDAhUZXN0Q2l0eTELMAkGA1UEBhMCVVMwggEiMA0GCSqGSIb3DQEBAQUAA4IB\nDwAwggEKAoIBAQDFajjrztId+ZQy/nqutDub/XHaOoPAPhY3EL67/CbzT/k530kg\nbN1MeQ7P3UPcHsPyfe2jws3IRPUqryLrx4FJtpcvjBVtYVUfcdwsABWicTLgcEAN\nYTZr/oBix6sedgyuTjdK7pPxXsi58/wQgfIScFs2YNaxCko53CKGn4WTjh0O2YQI\n4OVm7KO9MO8oxk4BeeK2L9Pa4EkS0F1ubVUGIgAypK2JTyvZHcA+zikXzqSVWh7V\nV4DU66hsr3NUHNhanAChR2QcxttN7q72pPTTpH9drChXnopNOtWsDeB16pxkGEj0\nJvDpm1wgw9wwnFmx+H1Wx0uQ8/Ug4VgszgCzAgMBAAGjUzBRMB0GA1UdDgQWBBQa\nCmALhNyShCacGDv4+o2/ypCuWDAfBgNVHSMEGDAWgBQaCmALhNyShCacGDv4+o2/\nypCuWDAPBgNVHRMBAf8EBTADAQH/MA0GCSqGSIb3DQEBCwUAA4IBAQA1nA6MiFmX\nQp91TbniZd1WfEOkB/f9JFhMiwhPPqrvtcackMXXpTKFVmAzk+Y/lADI/h114joX\noA4IrQH0/DZO3NNoAH+BhbQJdx4MquFbl9bzMC5FGgfVIgdx27dNv3zHuZcLs9k2\nUEtBF1j9kM0TDq4FJt1z/DN1lJLSIZHUzfNV6p94T11ppdT4BzuQlbb6B9eQKYPQ\n9LnReYO+PRBxIKStoUQ5Bjx8SzctFYO1aD/rnbbfAvMDVgku76uKTklTHJNVyppI\nokvKmhi9XdveB8OIOu13xaMlv4wIFpZNFPeHsSHIS3b0NzY4lM0kTmHvCvBzUgry\nSHZgVdY0WIu3\n-----END CERTIFICATE-----",
                "certificatePublicKeyAlgorithm": "RSA",
                "certificateSignatureAlgorithm": "SHA256withRSA"
            },
            "updatedA2aAgentCard": {
                "agentName": "TestAgent",
                "description": "Updated test agent for renewal",
                "capabilities": ["DocumentTranslation"],
                "endpoints": [
                    {"protocol": "http", "url": "http://localhost:9000/agent"}
                ]
            },
            "agentStatus": "active"
        }
    }

    print('\n--- Valid Renewal ---')
    response = requests.post(url, data=json.dumps(renewal), headers=headers)
    print('Status Code:', response.status_code)
    print('Response:', response.json())

    # Invalid certificate (not signed by CA)
    invalid_cert_renewal = json.loads(json.dumps(renewal))
    invalid_cert_renewal["requestingAgent"]["certificate"]["certificatePEM"] = """-----BEGIN CERTIFICATE-----\nMIIBsjCCAVugAwIBAgIUQ1RANDOMINVALID1234567890wDQYJKoZIhvcNAQELBQAwEjEQMA4GA1UEAwwHUmFuZG9tQ0EwHhcNMjUwNDE5MDAwMDAwWhcNMjYwNDE5MDAwMDAwWjASMRAwDgYDVQQDDAdSYW5kb21DQTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALo1w7zF1Q5+Qw4fK0F5RZBq9XwFZ2bT+3e3QwIDAQABo1MwUTAdBgNVHQ4EFgQU6QjvRANDOMINVALID1234567890wHwYDVR0jBBgwFoAU6QjvRANDOMINVALID1234567890wDwYDVR0TAQH/BAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAQEADummySignature==\n-----END CERTIFICATE-----"""
    print('\n--- Invalid Certificate (not signed by CA) ---')
    response = requests.post(url, data=json.dumps(invalid_cert_renewal), headers=headers)
    print('Status Code:', response.status_code)
    try:
        print('Response:', response.json())
    except Exception as e:
        print('Response could not be parsed:', e)

    # Invalid JSON
    print('\n--- Invalid JSON ---')
    response = requests.post(url, data='{bad json}', headers=headers)
    print('Status Code:', response.status_code)
    try:
        print('Response:', response.json())
    except Exception as e:
        print('Response could not be parsed:', e)

if __name__ == "__main__":
    test_renewal()
