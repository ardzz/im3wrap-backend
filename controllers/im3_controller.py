from flask import request
from flask_jwt_extended import get_jwt_identity

from core.error_handlers import logger
from core.response import SuccessResponse, ErrorResponse
from core.exceptions import ValidationError, AuthenticationError, NotFoundError
from models.user import User
from database import db
from im3.repository.authentication import Authentication
from im3.repository.profile import Profile
from .base_controller import validate_json, get_current_user_id


class IM3Controller:
    """IM3 integration controller"""

    def send_otp(self):
        """Send OTP to user's phone number"""
        try:
            user_id = get_current_user_id()
            if not user_id:
                raise AuthenticationError("Authentication required")

            user = User.query.get(user_id)
            if not user or not user.phone_number:
                raise ValidationError("Phone number is required")

            # Initialize IM3 authentication
            auth = Authentication(user.phone_number, debug=False)
            result = auth.send_otp()

            if result.get('status') == '0' or result.get('code') == '10006' or 'A code was sent to your mobile number XXX' in result.get('message'):
                # Store transaction ID for OTP verification
                user.transid = result.get('transid')
                db.session.commit()

                return SuccessResponse(
                    data={
                        "transid": result.get('transid'),
                        "message": "OTP sent successfully"
                    },
                    message="OTP sent to your phone number"
                ).to_response()
            else:
                raise ValidationError(f"Failed to send OTP: {result.get('message', 'Unknown error')}")

        except Exception as e:
            if isinstance(e, (ValidationError, AuthenticationError)):
                raise
            raise ValidationError(f"Failed to send OTP: {str(e)}")

    def verify_otp(self):
        """Verify OTP and get IM3 token"""
        try:
            user_id = get_current_user_id()
            if not user_id:
                raise AuthenticationError("Authentication required")

            user = User.query.get(user_id)
            if not user or not user.phone_number:
                raise ValidationError("Phone number is required")

            if not user.transid:
                raise ValidationError("OTP not sent. Please send OTP first.")

            # Get OTP code from request
            json_data = request.get_json()
            if not json_data or 'code' not in json_data:
                raise ValidationError("OTP code is required")

            otp_code = json_data['code']

            # Initialize IM3 authentication
            auth = Authentication(user.phone_number, debug=False)
            result = auth.verify_otp(user.transid, otp_code)

            if result.get('message') == 'Success' or result.get('code') == '10014':
                # Store the token ID
                logger.info(f"OTP verified successfully for user {user_id}: {result}")
                user.token_id = result.get('data')['tokenid']
                user.transid = None  # Clear transaction ID
                db.session.commit()

                return SuccessResponse(
                    data={
                        "verified": True,
                        "message": "OTP verified successfully"
                    },
                    message="IM3 account linked successfully"
                ).to_response()
            else:
                raise ValidationError(f"OTP verification failed: {result.get('message', 'Invalid OTP')}")

        except Exception as e:
            if isinstance(e, (ValidationError, AuthenticationError)):
                raise
            raise ValidationError(f"Failed to verify OTP: {str(e)}")

    def get_profile(self):
        """Get IM3 profile information"""
        try:
            user_id = get_current_user_id()
            if not user_id:
                raise AuthenticationError("Authentication required")

            user = User.query.get(user_id)
            if not user or not user.token_id:
                raise ValidationError("IM3 account not linked. Please verify OTP first.")

            # Get IM3 profile
            profile_service = Profile(user.token_id, debug=False)
            result = profile_service.get_profile()

            if result.get('message') == 'PROFILE_GET_USER_SUCCESS' or result.get('code') == '00':
                return SuccessResponse(
                    data=result.get('data', {}),
                    message="Profile retrieved successfully"
                ).to_response()
            else:
                raise ValidationError(f"Failed to get profile: {result.get('message', 'Unknown error')}")

        except Exception as e:
            if isinstance(e, (ValidationError, AuthenticationError)):
                raise
            raise ValidationError(f"Failed to get profile: {str(e)}")