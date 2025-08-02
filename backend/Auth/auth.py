from flask import jsonify, request
import requests
import dotenv
import os
from jose import jwt

dotenv.load_dotenv()

AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")
API_IDENTIFIER = os.environ.get("API_IDENTIFIER")
ALGORITHMS = ["RS256"]

# Get JWKS
jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
jwks = requests.get(jwks_url).json()

def get_token_auth_header():
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise Exception("Authorization header is missing.")
    parts = auth.split()
    if parts[0].lower() != "bearer":
        raise Exception("Authorization header must start with Bearer.")
    elif len(parts) == 1:
        raise Exception("Token not found.")
    elif len(parts) > 2:
        raise Exception("Authorization header must be Bearer token.")
    return parts[1]

def verify_jwt(token):
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
    if not rsa_key:
        raise Exception("No RSA key found.")
    
    payload = jwt.decode(
        token,
        rsa_key,
        algorithms=ALGORITHMS,
        audience=API_IDENTIFIER,
        issuer=f"https://{AUTH0_DOMAIN}/"
    )
    return payload

def requires_auth(f):
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
        try:
            payload = verify_jwt(token)
            return f(*args, **kwargs, user=payload)
        except Exception as e:
            return jsonify({"error": str(e)}), 401
    return decorated