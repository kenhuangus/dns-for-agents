# Agent DNS Discovery Tool

## Overview

The **Agent DNS Discovery Tool** (`discovery_tool.py`) acts as a decentralized "DNS" for agentic AI systems, enabling agents to discover and advertise capabilities in a secure, standards-compliant manner. It is designed for multi-agent environments using the A2A and MCP protocols, supporting robust schema validation and extensibility.

- **Discovery**: Agents can query for other agents with specific capabilities, domain expertise, or performance characteristics.
- **Advertisement**: Agents can register their capabilities, endpoints, and metadata so they can be discovered by others.
- **Compliance**: All requests and responses are validated against strict JSON Schemas, ensuring interoperability and security.

## How It Works

- Agents send a **discovery request** (e.g., "find me a DocumentTranslation agent for en-fr legal documents") using a JSON payload.
- The tool matches the request against registered agents and returns a schema-compliant response describing the best match.
- Agents can also **advertise** their own capabilities and endpoints, registering themselves for future discovery.
- The tool enforces all required fields (including certificates, A2A AgentCard, and MCP metadata) for both flows.

## Example Usage

### 1. Set Up the Environment

```sh
python -m venv venv
venv\Scripts\activate
pip install jsonschema
```

### 2. Run the Tool

```sh
python discovery_tool.py
```

### 3. Example Output

You should see output like:

```
Advertisement Response:
{
  "status": "success",
  ...
}

Discovery Response:
{
  "status": "success",
  ...
}
```

- The **Advertisement Response** confirms that an agent has registered successfully.
- The **Discovery Response** returns a matching agent profile, including its endpoint, capabilities, and cryptographic metadata.

## How to Test

1. **Advertisement**: The tool first registers a sample agent (`TranslatorB`) with full metadata (capabilities, endpoint, certificate, etc.).
2. **Discovery**: The tool then queries for an agent with `DocumentTranslation` capability, matching the registered agent.
3. **Validation**: All requests and responses are validated against the provided schemas. Any missing or invalid fields will result in a detailed error message.

You can modify the payloads in `discovery_tool.py` to test with your own agent profiles and queries.

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
