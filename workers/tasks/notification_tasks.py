from typing import Dict, Any, List, Optional
from datetime import datetime

from workers.base.base_task import BaseTask
from workers.base.task_status import TaskStatus
from workers.exceptions import TaskError


def register_notification_tasks(celery_app):
    """Register notification tasks with the Celery app"""

    @celery_app.task(bind=True, base=BaseTask, name='workers.tasks.send_notification')
    def send_notification_task(self, user_id: int, notification_type: str,
                               message: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send notification to user (email, SMS, push notification, etc.)
        """
        try:
            self.logger.info(f"Sending {notification_type} notification to user {user_id}")
            self.update_status(TaskStatus.PROCESSING, 20)

            # Validate notification type
            valid_types = ['email', 'sms', 'push', 'in_app']
            if notification_type not in valid_types:
                raise TaskError(f"Invalid notification type: {notification_type}")

            # Get user details
            from repositories.user_repository import UserRepository
            user_repo = UserRepository()
            user = user_repo.get_or_raise(user_id)

            self.update_status(TaskStatus.PROCESSING, 40)

            # Simulate different notification sending
            result = self._send_notification_by_type(
                notification_type, user, message, metadata or {}
            )

            self.update_status(TaskStatus.PROCESSING, 90)

            self.logger.info(f"Notification sent successfully to user {user_id}")

            return {
                "user_id": user_id,
                "notification_type": notification_type,
                "status": "sent",
                "sent_at": datetime.utcnow().isoformat(),
                "result": result
            }

        except Exception as e:
            self.logger.exception(f"Error sending notification: {e}")
            return self.handle_exception(e)

        def _send_notification_by_type(self, notification_type: str, user,
                                       message: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
            """Send notification based on type"""

            if notification_type == 'email':
                if not user.email:
                    raise TaskError("User has no email address")
                return self._send_email(user.email, message, metadata)

            elif notification_type == 'sms':
                if not user.phone_number:
                    raise TaskError("User has no phone number")
                return self._send_sms(user.phone_number, message, metadata)

            elif notification_type == 'push':
                return self._send_push_notification(user.id, message, metadata)

            elif notification_type == 'in_app':
                return self._create_in_app_notification(user.id, message, metadata)

            else:
                raise TaskError(f"Unsupported notification type: {notification_type}")

        def _send_email(self, email: str, message: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
            """Send email notification (placeholder implementation)"""
            # This would integrate with email service like SendGrid, SES, etc.
            self.logger.info(f"Sending email to {email}")

            return {
                "method": "email",
                "recipient": email,
                "subject": metadata.get('subject', 'IM3Wrap Notification'),
                "status": "sent",
                "provider": "mock_email_service"
            }

        def _send_sms(self, phone: str, message: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
            """Send SMS notification (placeholder implementation)"""
            # This would integrate with SMS service like Twilio, AWS SNS, etc.
            self.logger.info(f"Sending SMS to {phone}")

            return {
                "method": "sms",
                "recipient": phone,
                "message_length": len(message),
                "status": "sent",
                "provider": "mock_sms_service"
            }

        def _send_push_notification(self, user_id: int, message: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
            """Send push notification (placeholder implementation)"""
            # This would integrate with push service like FCM, APNS, etc.
            self.logger.info(f"Sending push notification to user {user_id}")

            return {
                "method": "push",
                "user_id": user_id,
                "title": metadata.get('title', 'IM3Wrap'),
                "status": "sent",
                "provider": "mock_push_service"
            }

        def _create_in_app_notification(self, user_id: int, message: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
            """Create in-app notification (placeholder implementation)"""
            # This would create a database record for in-app notifications
            self.logger.info(f"Creating in-app notification for user {user_id}")

            return {
                "method": "in_app",
                "user_id": user_id,
                "message": message,
                "status": "created",
                "read": False
            }

    @celery_app.task(bind=True, base=BaseTask, name='workers.tasks.send_bulk_notifications')
    def send_bulk_notifications_task(self, user_ids: List[int], notification_type: str,
                                     message: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send bulk notifications to multiple users
        """
        try:
            total_users = len(user_ids)
            self.logger.info(f"Sending bulk {notification_type} notifications to {total_users} users")
            self.update_status(TaskStatus.PROCESSING, 5)

            successful_sends = 0
            failed_sends = 0
            results = []

            for i, user_id in enumerate(user_ids):
                try:
                    # Queue individual notification task
                    task = send_notification_task.delay(user_id, notification_type, message, metadata)
                    results.append({
                        "user_id": user_id,
                        "task_id": task.id,
                        "status": "queued"
                    })
                    successful_sends += 1

                except Exception as e:
                    self.logger.error(f"Failed to queue notification for user {user_id}: {e}")
                    results.append({
                        "user_id": user_id,
                        "status": "failed",
                        "error": str(e)
                    })
                    failed_sends += 1

                # Update progress
                progress = int((i + 1) / total_users * 90) + 5
                self.update_status(TaskStatus.PROCESSING, progress)

            self.logger.info(f"Bulk notification queuing complete: {successful_sends} queued, {failed_sends} failed")

            return {
                "total_users": total_users,
                "successful_queues": successful_sends,
                "failed_queues": failed_sends,
                "notification_type": notification_type,
                "queued_at": datetime.now().isoformat(),
                "results": results
            }

        except Exception as e:
            self.logger.exception(f"Error in bulk notification task: {e}")
            return self.handle_exception(e)

    return send_notification_task, send_bulk_notifications_task