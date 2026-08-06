import base64
import hashlib
import secrets

def generate_pkce() -> tuple[str, str]:
    """
    Generate PKCE values for OAuth authorization.

    Returns:
        A tuple containing:
        - code_verifier: random secret kept locally by the client.
        - code_challenge: SHA256-based value sent to the authorization server.
    """
    verifier = base64.urlsafe_b64encode(
        secrets.token_bytes(32)
    ).rstrip(b"=").decode("ascii")

    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode("ascii")).digest()
    ).rstrip(b"=").decode("ascii")

    return verifier, challenge