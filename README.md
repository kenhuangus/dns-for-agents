# Agent Registration & Discovery System

## Overview
A secure registry and management API for multi-agent AI systems. Agents can register, renew, deactivate, and query their status, all with strong JSON Schema and certificate validation.

---

## Features
- **Agent Registration** (`/register`): Agents register with a valid certificate and metadata.
- **Agent Renewal** (`/renew`): Agents renew their registration and update capabilities.
- **Agent Deactivation** (`/deactivate`): Deactivate an agent by name (marks as inactive).
- **Status Query** (`/status?agentName=...`): Query the current status (`active`/`inactive`) of any agent.
- **Robust Validation**: All requests validated against JSON Schemas. Certificates must be signed by your local CA.

---

## Setup

```sh
python -m venv venv
venv\Scripts\activate
pip install jsonschema cryptography requests
```

### Generate Certificates (for Secure Trust)
```sh
# Root CA
openssl genrsa -out ca.key 2048
openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 -out ca.pem -subj "/CN=Test Root CA/OU=TestCA/O=TestOrg/L=TestCity/C=US"
# Agent
openssl genrsa -out agent.key 2048
openssl req -new -key agent.key -out agent.csr -subj "/CN=TranslatorB/OU=Agents/O=MyOrg/L=City/C=US"
openssl x509 -req -in agent.csr -CA ca.pem -CAkey ca.key -CAcreateserial -out agent.pem -days 365 -sha256
```

---

## API Endpoints

### 1. Registration
- **Endpoint:** `POST /register`
- **Schema:** `agent_registration_request_schema.json`
- **Description:** Register a new agent with metadata and a valid certificate.

### 2. Renewal
- **Endpoint:** `POST /renew`
- **Schema:** `agent_renewal_request_schema.json`
- **Description:** Renew an agent's registration and update capabilities/certificate.

### 3. Deactivation
- **Endpoint:** `POST /deactivate`
- **Schema:** `agent_deactivation_request_schema.json`
- **Description:** Deactivate (set status to inactive) an agent by name.

### 4. Status Query
- **Endpoint:** `GET /status?agentName=...`
- **Description:** Query current status (`active`/`inactive`) of any agent.

---

## JSON Schema Files
- All schemas are in the project root and define request/response formats for each endpoint.
- Update schemas to add/modify required agent metadata as needed.

---

## Running the APIs
Each API runs on its own port. In separate terminals:
```sh
python agent_registration_api.py   # (default: 8080)
python agent_renewal_api.py        # (default: 8081)
python agent_deactivation_api.py   # (default: 8082)
python agent_status_api.py         # (default: 8083)
```

---

## Testing
Test scripts are provided for each endpoint:
```sh
python test_registration_api.py
python test_renewal_api.py
python test_deactivation_api.py
python test_status_api.py
```
Each script tests valid, invalid, and edge-case scenarios. Review output for status codes and messages.

---

## Security Considerations
- **Certificate Validation:** All registration and renewal requests require a valid agent certificate signed by your local CA (`ca.pem`).
- **Authentication:** (Optional, not yet implemented) You can add API Key, Bearer Token, or Mutual TLS authentication for additional security.
- **Database:** All agent data is stored in `agent_registration.db` (SQLite, local).

---

## Extending & Customizing
- To add new agent metadata or validation logic, update the corresponding JSON schema and handler.
- To add authentication, see the README section on authentication options.

---

## License
MIT


## JSON Schema Files

This tool validates all agent requests and responses using two external JSON Schema files:

- `agent_capability_request.schema.json`: Defines the required structure for agent discovery and advertisement requests.
- `agent_capability_response.schema.json`: Defines the required structure for responses to those requests.

**Location:** Both files are in the project root directory. You can open and edit them with any text editor or JSON tool.

**Purpose:**
- Ensure all agent messages are well-formed and standards-compliant.
- Make it easy to extend the protocol for new agent types, capabilities, or metadata fields. Just update the schema files as needed.

**How to Update:**
- To add new required agent metadata, add properties to the appropriate schema file.
- To relax or tighten validation, edit types, required fields, or allowed values in the schema.
- After editing, re-run the tool and tests to confirm everything works as expected.

---

## Main Usage Example

### 1. Environment Setup

```sh
python -m venv venv
venv\Scripts\activate
pip install jsonschema cryptography
```

### 2. Generate Certificates (for Secure Trust)

```sh
# Root CA
openssl genrsa -out ca.key 2048
openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 -out ca.pem -subj "/CN=Test Root CA/OU=TestCA/O=TestOrg/L=TestCity/C=US"
# Agent
openssl genrsa -out agent.key 2048
openssl req -new -key agent.key -out agent.csr -subj "/CN=TranslatorB/OU=Agents/O=MyOrg/L=City/C=US"
openssl x509 -req -in agent.csr -CA ca.pem -CAkey ca.key -CAcreateserial -out agent.pem -days 365 -sha256
```

### 3. Run the Main Tool

```sh
python discovery_tool.py
```

### 4. Example: Programmatic Usage

```python
from discovery_tool import AgentDiscoveryTool, AGENT_CAPABILITY_REQUEST_SCHEMA, AGENT_CAPABILITY_RESPONSE_SCHEMA

# Load CA
tool = AgentDiscoveryTool(AGENT_CAPABILITY_REQUEST_SCHEMA, AGENT_CAPABILITY_RESPONSE_SCHEMA, ca_cert_path="ca.pem")

# Load agent cert
with open("agent.pem") as f:
    agent_cert_pem = f.read()

# Advertisement payload
adv_payload = {
    "requestType": "advertisement",
    "requestingAgent": {
        "agentName": "TranslatorB",
        ...
        "certificate": {
            ...
            "certificatePEM": agent_cert_pem,
        },
        ...
    }
}
resp = tool.handle_advertisement(adv_payload, {})
print(resp)

# Discovery payload (see test_discovery_tool.py for details)
```

---

## Automated Testing

A full test script is included:

```sh
python test_discovery_tool.py
```

This script exercises both advertisement and discovery flows with real certificate validation. If you tamper with certificates or CA, the tool will reject the agent.

---

## How to Contribute

Contributions are welcome! Please see the [Contributing Guidelines](CONTRIBUTING.md) and open issues or pull requests for improvements.

## License

This project is licensed under the [MIT License](LICENSE).

## Disclaimer & No Liability

This software is provided "as is", without warranty of any kind, express or implied. The authors and contributors shall not be held liable for any damages or losses arising from the use of this software. Use at your own risk.

---

## How to Test Certificates (Step-by-Step)

### 1. Generate a Local CA and Agent Certificate

Open a terminal in your project directory and run:

```sh
# Generate CA private key and self-signed certificate
openssl genrsa -out ca.key 2048
openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 -out ca.pem -subj "/CN=Test Root CA/OU=TestCA/O=TestOrg/L=TestCity/C=US"

# Generate agent private key and CSR
openssl genrsa -out agent.key 2048
openssl req -new -key agent.key -out agent.csr -subj "/CN=TranslatorB/OU=Agents/O=MyOrg/L=City/C=US"

# Sign agent certificate with CA
openssl x509 -req -in agent.csr -CA ca.pem -CAkey ca.key -CAcreateserial -out agent.pem -days 365 -sha256
```

- `ca.pem` — Root CA certificate (trusted by your tool)
- `agent.pem` — Agent certificate (used in payloads)

### 2. How the Tool Uses Certificates

- The tool loads `ca.pem` as the trusted CA.
- When an agent advertises or is discovered, its `certificatePEM` field is checked:
  - **Signature is validated** against the CA.
  - **Validity period** is checked.
  - If invalid, the request/agent is rejected.

### 3. Automated Test

Run the provided test script to verify certificate validation:

```sh
python test_discovery_tool.py
```

You should see both Advertisement and Discovery succeed. If you tamper with the certificate or CA, the tool will reject the request.

### 4. Testing with Your Own Agents

Repeat the certificate generation steps for each new agent, and update the tool/test payloads with the new certificate PEM.

---

**Note:** For production, always use secure storage for private keys and certificates.

## Security & Best Practices

- **Certificates**: For demo purposes, PEM certificates are included as strings. In production, use secure vaults and references.
- **Schema Validation**: Strict validation prevents malformed or malicious payloads.
- **Extensibility**: The tool supports additional agent metadata and custom query parameters.

## Why "Agent DNS"?

Just as DNS allows computers to find each other on the internet, this tool allows agents to discover and verify each other's capabilities, endpoints, and trust credentials in a secure, decentralized fashion.

---

For advanced integration, see the code for how to extend the registry, add REST APIs, or connect to real credential vaults.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for the full license text.

## How to Contribute

Contributions are welcome! If you have suggestions, bug reports, or would like to submit a pull request, please:
- Open an issue describing your proposed change or bug.
- Fork the repository and submit a pull request with your improvements.
- Follow the project's code style and testing guidelines.

## Disclaimer & No Liability

This software is provided "as is", without warranty of any kind, express or implied. The authors and contributors shall not be held liable for any damages or losses arising from the use of this software. Use at your own risk.
