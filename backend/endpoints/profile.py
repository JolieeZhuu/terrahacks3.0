from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from Auth.auth import *

db = SQLAlchemy()
from models.User import User

def create_get_user(payload):
    try:
        auth0_id = payload.get('sub')
        email = payload.get('email')
        name = payload.get('name')

        user = User.query.filter_by(auth0_id=auth0_id).first()

        if not user:
            user = User(auth0_id=auth0_id, email=email, name=name)
            db.session.add(user)
            db.session.commit()

        return jsonify ({
            "message": "User profile retrieved successfully",
            "user": {
                "id": user.id,
                "auth0_id": user.auth0_id,
                "email": user.email,
                "name": user.name
            }
        })
    except Exception as e:
        return jsonify(error=str(e)), 500