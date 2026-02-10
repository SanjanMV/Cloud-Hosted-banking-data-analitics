import boto3
import os
from flask import current_app
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, app_config):
        self.sns_client = None
        self.twilio_client = None

        # Initialize SNS client for email
        if app_config.get('ENABLE_EMAIL_NOTIFICATIONS'):
            try:
                self.sns_client = boto3.client(
                    'sns',
                    region_name=app_config['AWS_REGION'],
                    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
                )
                logger.info("SNS client initialized for email notifications")
            except Exception as e:
                logger.error(f"Failed to initialize SNS client: {e}")

        # Initialize Twilio client for SMS
        if app_config.get('ENABLE_SMS_NOTIFICATIONS'):
            try:
                account_sid = app_config.get('TWILIO_ACCOUNT_SID')
                auth_token = app_config.get('TWILIO_AUTH_TOKEN')
                if account_sid and auth_token:
                    self.twilio_client = Client(account_sid, auth_token)
                    logger.info("Twilio client initialized for SMS notifications")
                else:
                    logger.warning("Twilio credentials not configured")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")

    def send_sms(self, to_phone, message):
        """Send SMS notification using Twilio"""
        if not self.twilio_client or not current_app.config.get('ENABLE_SMS_NOTIFICATIONS'):
            logger.info("SMS notifications disabled or not configured")
            return False

        try:
            from_number = current_app.config.get('TWILIO_PHONE_NUMBER')
            if not from_number:
                logger.error("Twilio phone number not configured")
                return False

            message = self.twilio_client.messages.create(
                body=message,
                from_=from_number,
                to=to_phone
            )
            logger.info(f"SMS sent successfully to {to_phone}")
            return True
        except TwilioException as e:
            logger.error(f"Failed to send SMS: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending SMS: {e}")
            return False

    def send_email(self, to_email, subject, body):
        """Send email notification using AWS SNS"""
        if not self.sns_client or not current_app.config.get('ENABLE_EMAIL_NOTIFICATIONS'):
            logger.info("Email notifications disabled or not configured")
            return False

        try:
            topic_arn = current_app.config.get('SNS_TOPIC_ARN')
            if not topic_arn:
                logger.error("SNS topic ARN not configured")
                return False

            # Publish message to SNS topic with email as message attribute
            response = self.sns_client.publish(
                TopicArn=topic_arn,
                Subject=subject,
                Message=body,
                MessageAttributes={
                    'email': {
                        'DataType': 'String',
                        'StringValue': to_email
                    }
                }
            )
            logger.info(f"Email notification published to SNS for {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish email notification: {e}")
            return False

# Global notification service instance - will be initialized in app factory
notification_service = None

def send_transaction_notification(user_email, user_phone, transaction_type, amount, balance=None):
    """Send notifications for banking transactions"""
    from flask import current_app

    # Format the message
    amount_str = f"${amount:.2f}"
    message = f"Your account {transaction_type} of {amount_str} has been processed."

    if balance is not None:
        message += f" Current balance: ${balance:.2f}"

    subject = f"Bank Transaction Notification - {transaction_type.title()}"

    # Send SMS if enabled and phone provided
    if user_phone:
        sms_sent = current_app.notification_service.send_sms(user_phone, message)
        if sms_sent:
            logger.info(f"SMS notification sent for {transaction_type}")
        else:
            logger.warning(f"Failed to send SMS notification for {transaction_type}")

    # Send email if enabled
    if user_email:
        email_sent = current_app.notification_service.send_email(user_email, subject, message)
        if email_sent:
            logger.info(f"Email notification sent for {transaction_type}")
        else:
            logger.warning(f"Failed to send email notification for {transaction_type}")

def send_security_notification(user_email, user_phone, event_type, details=""):
    """Send security-related notifications"""
    from flask import current_app

    message = f"Security Alert: {event_type}"
    if details:
        message += f" - {details}"

    subject = f"Security Notification - {event_type}"

    # Send SMS for security alerts (high priority)
    if user_phone:
        sms_sent = current_app.notification_service.send_sms(user_phone, f"SECURITY: {message}")
        if sms_sent:
            logger.info(f"Security SMS sent for {event_type}")
        else:
            logger.warning(f"Failed to send security SMS for {event_type}")

    # Send email
    if user_email:
        email_sent = current_app.notification_service.send_email(user_email, subject, message)
        if email_sent:
            logger.info(f"Security email sent for {event_type}")
        else:
            logger.warning(f"Failed to send security email for {event_type}")
