"""
Mitigation Example 3: Strong Authentication & Authorization
Uses JWT and environment-based credentials to ensure agent identity and secure operations.
"""
from samples.python.common.types import AuthenticationInfo
import os
from jose import jwt, JWTError

# Note: Functions in this file expect agent identifier fields: protocol, agentName, agentCategory, providerName, version, extension (optional) where relevant.
def validate_jwt(token, public_key, audience):
    try:
        payload = jwt.decode(token, public_key, audience=audience, algorithms=['RS256'])
        return payload
    except JWTError:
        raise ValueError('Invalid or expired token')

def get_authentication_info() -> AuthenticationInfo:
    token = os.environ.get("A2A_TOKEN")
    if not token:
        raise EnvironmentError("A2A_TOKEN not set")
    return AuthenticationInfo(schemes=["bearer"], credentials=token)

def test_get_authentication_info():
    os.environ["A2A_TOKEN"] = "dummy-token"
    auth_info = get_authentication_info()
    assert auth_info.schemes == ["bearer"]
    assert auth_info.credentials == "dummy-token"
    del os.environ["A2A_TOKEN"]
    try:
        get_authentication_info()
    except EnvironmentError as e:
        assert "A2A_TOKEN not set" in str(e)
    else:
        raise AssertionError("Expected EnvironmentError when token is missing")

if __name__ == "__main__":
    test_get_authentication_info()
    print("Authentication & authorization example ran successfully.")
