"""
Mitigation Example 8: Continuous Auditing & Credential Hygiene
Shows how to rotate credentials and maintain secure authentication info.
"""
import os
import secrets
from samples.python.common.types import AuthenticationInfo

# Note: Credential hygiene routines may reference agent identifier fields: protocol, agentName, agentCategory, providerName, version, extension (optional) for context.
def rotate_credential(key: str):
    new_value = secrets.token_hex(16)
    os.environ[key] = new_value
    return new_value

def audit_credential(key: str):
    val = os.environ.get(key)
    if not val:
        raise EnvironmentError(f"Credential {key} missing!")
    return val

def test_credential_hygiene():
    key = "A2A_TOKEN"
    old = rotate_credential(key)
    assert audit_credential(key) == old
    new = rotate_credential(key)
    assert audit_credential(key) == new

if __name__ == "__main__":
    test_credential_hygiene()
    print("Credential hygiene example ran successfully.")
