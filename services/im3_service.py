from typing import Dict, Any
from .base_service import BaseService
from repositories.user_repository import UserRepository
from models.user import User
from im3.repository.authentication import Authentication
from im3.repository.profile import Profile
from core.exceptions import (
    ValidationError,
    IM3AuthError,
    BusinessLogicError
)


class IM3Service(BaseService[User]):
    """IM3 integration service"""

    def __init__(self):
        super().__init__(UserRepository())

    def send_otp(self, user_id: int) -> Dict[str, str]:
        """Send OTP to user's phone number"""
        user = self.repository.get_or_raise(user_id)

        if not user.phone_number:
            raise ValidationError("Phone number is not set for this user")

        try:
            im3auth = Authentication(user.phone_number)
            response = im3auth.send_otp()

            if response.get('status') != '0':
                self.logger.error(f"IM3 OTP send failed for user {user_id}: {response}")
                raise IM3AuthError(response.get('message', 'Failed to send OTP'))

            # Store transaction ID
            transid = response['data']['transid']
            self.repository.update(user, transid=transid)

            self.logger.info(f"OTP sent successfully for user {user_id}")

            return {"message": response['message']}

        except Exception as e:
            self.logger.error(f"Error sending OTP for user {user_id}: {str(e)}")
            if isinstance(e, IM3AuthError):
                raise
            raise IM3AuthError(f"Failed to send OTP: {str(e)}")

    def verify_otp(self, user_id: int, otp_code: str) -> Dict[str, str]:
        """Verify OTP code"""
        user = self.repository.get_or_raise(user_id)

        if not user.phone_number:
            raise ValidationError("Phone number is not set for this user")

        if not user.transid:
            raise BusinessLogicError("No OTP request found. Please request OTP first")

        if not otp_code or not otp_code.isdigit():
            raise ValidationError("Invalid OTP code format")

        try:
            im3auth = Authentication(user.phone_number)
            response = im3auth.verify_otp(user.transid, int(otp_code))

            if response.get('status') != '0':
                self.logger.warning(f"IM3 OTP verification failed for user {user_id}: {response}")
                raise IM3AuthError(response.get('message', 'OTP verification failed'))

            # Store token ID and clear transaction ID
            token_id = response['data']['tokenid']
            self.repository.update(user, token_id=token_id, transid=None)

            self.logger.info(f"OTP verified successfully for user {user_id}")

            return {"message": response['message']}

        except Exception as e:
            self.logger.error(f"Error verifying OTP for user {user_id}: {str(e)}")
            if isinstance(e, (IM3AuthError, ValidationError, BusinessLogicError)):
                raise
            raise IM3AuthError(f"Failed to verify OTP: {str(e)}")

    def get_im3_profile(self, user_id: int) -> Dict[str, Any]:
        """Get IM3 profile data"""
        user = self.repository.get_or_raise(user_id)

        if not user.token_id:
            raise BusinessLogicError("User is not authenticated with IM3. Please verify OTP first")

        try:
            im3profile = Profile(token_id=user.token_id)
            response = im3profile.get_profile()

            if response.get('status') != '0':
                self.logger.error(f"IM3 profile fetch failed for user {user_id}: {response}")
                raise IM3AuthError(response.get('message', 'Failed to fetch profile'))

            self.logger.info(f"IM3 profile fetched successfully for user {user_id}")

            return response['data']

        except Exception as e:
            self.logger.error(f"Error fetching IM3 profile for user {user_id}: {str(e)}")
            if isinstance(e, (IM3AuthError, BusinessLogicError)):
                raise
            raise IM3AuthError(f"Failed to fetch profile: {str(e)}")