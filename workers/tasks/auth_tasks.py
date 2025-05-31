from typing import Dict, Any, List
from datetime import datetime, timedelta

from workers.base.base_task import BaseTask
from workers.base.task_status import TaskStatus
from repositories.user_repository import UserRepository


def register_auth_tasks(celery_app):
    """Register auth tasks with the Celery app"""

    @celery_app.task(bind=True, base=BaseTask, name='workers.tasks.cleanup_expired_tokens')
    def cleanup_expired_tokens_task(self) -> Dict[str, Any]:
        """
        Cleanup expired IM3 tokens and transaction IDs
        """
        try:
            self.logger.info("Starting cleanup of expired tokens")
            self.update_status(TaskStatus.PROCESSING, 10)

            user_repo = UserRepository()

            # Find users with old transaction IDs (older than 24 hours)
            cutoff_time = datetime.utcnow() - timedelta(hours=24)

            # This is a simplified cleanup - in real implementation, you'd check actual token expiry
            users_with_old_transids = user_repo.session.query(user_repo.model).filter(
                user_repo.model.transid.isnot(None),
                user_repo.model.updated_at < cutoff_time
            ).all()

            self.update_status(TaskStatus.PROCESSING, 50)

            cleaned_count = 0
            for user in users_with_old_transids:
                user.transid = None
                cleaned_count += 1

            user_repo.session.commit()

            self.update_status(TaskStatus.PROCESSING, 90)

            self.logger.info(f"Cleaned up {cleaned_count} expired transaction IDs")

            return {
                "cleaned_transids": cleaned_count,
                "processed_at": datetime.utcnow().isoformat(),
                "cutoff_time": cutoff_time.isoformat()
            }

        except Exception as e:
            self.logger.exception(f"Error during token cleanup: {e}")
            return self.handle_exception(e)

    @celery_app.task(bind=True, base=BaseTask, name='workers.tasks.validate_im3_tokens')
    def validate_im3_tokens_task(self, batch_size: int = 100) -> Dict[str, Any]:
        """
        Validate IM3 tokens by making test API calls
        """
        try:
            self.logger.info(f"Starting IM3 token validation with batch size {batch_size}")
            self.update_status(TaskStatus.PROCESSING, 5)

            user_repo = UserRepository()

            # Get users with token_id
            users_with_tokens = user_repo.session.query(user_repo.model).filter(
                user_repo.model.token_id.isnot(None)
            ).limit(batch_size).all()

            total_users = len(users_with_tokens)
            if total_users == 0:
                return {"message": "No users with tokens to validate"}

            valid_tokens = 0
            invalid_tokens = 0

            for i, user in enumerate(users_with_tokens):
                try:
                    # Import here to avoid circular imports
                    from im3.repository.profile import Profile

                    profile_service = Profile(token_id=user.token_id)
                    response = profile_service.get_profile()

                    if response.get('status') == '0':
                        valid_tokens += 1
                    else:
                        invalid_tokens += 1
                        # Optionally clear invalid token
                        # user.token_id = None

                    # Update progress
                    progress = int((i + 1) / total_users * 85) + 10
                    self.update_status(TaskStatus.PROCESSING, progress)

                except Exception as e:
                    self.logger.warning(f"Failed to validate token for user {user.id}: {e}")
                    invalid_tokens += 1

            # user_repo.session.commit()  # Uncomment if clearing invalid tokens

            self.logger.info(f"Token validation complete: {valid_tokens} valid, {invalid_tokens} invalid")

            return {
                "total_checked": total_users,
                "valid_tokens": valid_tokens,
                "invalid_tokens": invalid_tokens,
                "validation_time": datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.exception(f"Error during token validation: {e}")
            return self.handle_exception(e)

    return cleanup_expired_tokens_task, validate_im3_tokens_task