from flask import Flask, jsonify, request
from flask_cors import CORS
from Auth.auth import get_token_auth_header, verify_jwt, requires_auth
from config import Config


app = Flask(__name__)
CORS(app)  # allow requests from React (localhost:5173)


# Auth Login Routes

@app.route("/api/protected")
@requires_auth
def protected():
    try:
        token = get_token_auth_header()
        payload = verify_jwt(token)
        return jsonify(message="Access granted!", user=payload)
    except Exception as e:
        return jsonify(error=str(e)), 401

@app.route("/api/hello")
def hello():
    return jsonify(message="Public hello")

if __name__ == "__main__":
    app.run(debug=True)
