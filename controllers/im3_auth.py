from flask import jsonify, request

from database import db
from im3.repository.authentication import Authentication
from im3.repository.profile import Profile
from models.user import User


class IM3Auth:
    @staticmethod
    def send_otp():
        try:
            me = User.query.filter_by(id=request.user_id).first()
            if me.phone_number is None:
                return jsonify({"error": "Phone number is not set"}), 400
            else:
                im3auth = Authentication(me.phone_number)
                response = im3auth.send_otp()
                if response['status'] == '0':
                    me.transid = response['data']['transid']
                    db.session.commit()
                    return jsonify({"message": response['message']}), 200
                else:
                    return jsonify({"error": response['message']}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @staticmethod
    def verify_otp():
        try:
            me = User.query.filter_by(id=request.user_id).first()
            if me.phone_number is None:
                return jsonify({"error": "Phone number is not set"}), 400
            elif me.transid is None:
                return jsonify({"error": "You haven't requested OTP"}), 400
            else:
                im3auth = Authentication(me.phone_number)
                verify = im3auth.verify_otp(me.transid, int(request.json['code']))
                if verify['status'] == '0':
                    me.transid = None
                    me.token_id = verify['data']['tokenid']
                    db.session.commit()
                    return jsonify({"message": verify['message']}), 200
                else:
                    return jsonify({"error": verify['message']}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @staticmethod
    def get_profile():
        try:
            me = User.query.filter_by(id=request.user_id).first()
            if me.token_id is None:
                return jsonify({"error": "You haven't logged in"}), 400
            else:
                im3profile = Profile(token_id=me.token_id)
                profile = im3profile.get_profile()
                if profile['status'] == '0':
                    return jsonify(profile['data']), 200
                else:
                    return jsonify({"error": profile['message']}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 400