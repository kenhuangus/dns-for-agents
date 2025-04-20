# Agent DNS Discovery Tool

## What is This?

The **Agent DNS Discovery Tool** is a secure, standards-compliant registry and lookup service for multi-agent AI systems. It acts as a decentralized "DNS for Agents," enabling agents to:
- **Advertise** their capabilities, endpoints, and credentials
- **Discover** other agents matching specific needs (e.g., translation, domain expertise, performance)

This tool is built for environments using the A2A (Agent-to-Agent) and MCP (Multi-Agent Collaboration Protocol) standards, with robust JSON Schema and cryptographic certificate validation.

---

## Architecture

```mermaid
graph TD
    subgraph Agent DNS Discovery Tool
      DT[Discovery Tool]
      REG[Agent Registry]
      SCHEMA[JSON Schema Validator]
      CERT[Certificate Validator]
    end

    AG1[Agent A (Advertiser)] -- Advertise Capabilities --> DT
    AG2[Agent B (Discoverer)] -- Discovery Request --> DT
    DT -- Schema Validation --> SCHEMA
    DT -- Cert Validation --> CERT
    DT -- Register/Lookup --> REG
    DT -- Discovery Response --> AG2
    DT -- Advertisement Response --> AG1
```

- Agents interact with the tool via JSON payloads (discovery/advertisement)
- All requests and responses are validated for structure and trust
- The registry is extensible for new agent types and metadata

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
