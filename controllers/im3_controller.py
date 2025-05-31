from services.im3_service import IM3Service
from schemas.im3_schemas import VerifyOTPSchema
from core.response import SuccessResponse
from .base_controller import validate_json, get_current_user_id


class IM3Controller:
    """IM3 integration controller"""

    def __init__(self):
        self.im3_service = IM3Service()

    def send_otp(self):
        """Send OTP to user's phone number"""
        user_id = get_current_user_id()
        result = self.im3_service.send_otp(user_id)

        return SuccessResponse(
            data=result,
            message="OTP sent successfully"
        ).to_response()

    @validate_json(VerifyOTPSchema)
    def verify_otp(self, validated_data: dict):
        """Verify OTP code"""
        user_id = get_current_user_id()
        result = self.im3_service.verify_otp(
            user_id=user_id,
            otp_code=validated_data['code']
        )

        return SuccessResponse(
            data=result,
            message="OTP verified successfully"
        ).to_response()

    def get_profile(self):
        """Get IM3 profile data"""
        user_id = get_current_user_id()
        profile = self.im3_service.get_im3_profile(user_id)

        return SuccessResponse(
            data=profile,
            message="IM3 profile retrieved successfully"
        ).to_response()