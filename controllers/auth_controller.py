from flask import jsonify, request
from flask_jwt_extended import create_access_token
from database import db
from forms.auth_form import RegistrationForm, LoginForm
from models.user import User


class AuthController:
    @staticmethod
    def register():
        form = RegistrationForm(data=request.get_json())

        if not form.validate():
            return jsonify({"errors": form.errors}), 400
        if User.query.filter_by(username=form.username.data).first():
            return jsonify({"error": "Username already exists"}), 409

        new_user = User(
            username=form.username.data,
        )
        new_user.hash_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User registered", "user_id": new_user.id}), 201

    @staticmethod
    def login():
        form = LoginForm(data=request.get_json())

        if not form.validate():
            return jsonify({"errors": form.errors}), 400

        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            access_token = create_access_token(identity=str(user.id), expires_delta=False)
            return jsonify({"access_token": access_token}), 200

        return jsonify({"error": "Invalid credentials"}), 401