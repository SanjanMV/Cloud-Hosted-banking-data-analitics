import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    DYNAMODB_TABLE_USERS = 'BankingUsers'
    DYNAMODB_TABLE_ACCOUNTS = 'BankingAccounts'
    DYNAMODB_TABLE_TRANSACTIONS = 'BankingTransactions'
    # Use local DynamoDB only if explicitly set in environment and not localhost (for docker)
    endpoint = os.getenv('DYNAMODB_ENDPOINT_URL')
    DYNAMODB_ENDPOINT_URL = endpoint if endpoint and endpoint != 'http://localhost:8000' else None

    # Notification settings
    ENABLE_EMAIL_NOTIFICATIONS = os.getenv('ENABLE_EMAIL_NOTIFICATIONS', 'false').lower() == 'true'
    ENABLE_SMS_NOTIFICATIONS = os.getenv('ENABLE_SMS_NOTIFICATIONS', 'false').lower() == 'true'
    SNS_TOPIC_ARN = os.getenv('SNS_TOPIC_ARN')
    NOTIFICATION_EMAIL = os.getenv('NOTIFICATION_EMAIL', 'noreply@yourbank.com')
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

    # AWS settings
    USE_REAL_AWS = os.getenv('USE_REAL_AWS', 'false').lower() == 'true'
