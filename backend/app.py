from flask import Flask, jsonify, request
from flask_cors import CORS
from Auth.auth import get_token_auth_header, verify_jwt, requires_auth
from config import Config
from flask_sqlalchemy import SQLAlchemy

# Import Routes
from endpoints.profile import create_get_user

db = SQLAlchemy()

app = Flask(__name__)
CORS(app)  # allow requests from React (localhost:5173)

# Update with your database URL
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db" 
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


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

@app.route("/api/user_profile", methods=['POST', 'GET'])
def user_profile(payload):
    return create_get_user(payload)

if __name__ == "__main__":
    app.run(debug=True)
