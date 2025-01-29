from flask import jsonify, request

from database import db
from models.user import User


class UserController:
    @staticmethod
    def get_me():
        get_user = User.query.filter_by(id=request.user_id).first()
        return jsonify({
            "id": get_user.id,
            "username": get_user.username,
            "email": get_user.email,
        }), 200

    @staticmethod
    def update_me():
        try:
            me = User.query.filter_by(id=request.user_id).first()
            me.username = request.json.get('username', me.username)
            me.email = request.json.get('email', me.email)
            me.phone_number = request.json.get('phone_number', me.phone_number)

            db.session.commit()

            return jsonify({
                "id": me.id,
                "username": me.username,
                "email": me.email,
                "phone_number": me.phone_number,
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400

    @staticmethod
    def change_password():
        try:
            me = User.query.filter_by(id=request.user_id).first()
            if not me.check_password(request.json.get('old_password')):
                return jsonify({"error": "Old password is incorrect"}), 400

            me.set_password(request.json.get('new_password'))
            db.session.commit()

            return jsonify({"message": "Password updated"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400