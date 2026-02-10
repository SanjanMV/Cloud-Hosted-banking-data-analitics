from flask import Flask
from flask_login import LoginManager
import boto3
from config import Config
import os

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

# Global variable to track if moto has been started
_moto_started = False

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.get(user_id)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Determine if we should use moto for local development
    use_moto = (os.getenv('FLASK_ENV') == 'development' and
                not os.getenv('USE_REAL_AWS', 'false').lower() == 'true')

    # Initialize DynamoDB
    if use_moto:
        # Use moto for local development
        global _moto_started
        if not _moto_started:
            from moto import mock_dynamodb
            mock = mock_dynamodb()
            mock.start()
            _moto_started = True
        aws_access_key_id = 'testing'
        aws_secret_access_key = 'testing'
    else:
        # Use real AWS credentials
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

    dynamodb_kwargs = {
        'region_name': app.config['AWS_REGION'],
        'aws_access_key_id': aws_access_key_id,
        'aws_secret_access_key': aws_secret_access_key
    }
    app.dynamodb = boto3.resource('dynamodb', **dynamodb_kwargs)

    # Create tables if they don't exist
    try:
        app.dynamodb.create_table(
            TableName=app.config['DYNAMODB_TABLE_USERS'],
            KeySchema=[{'AttributeName': 'user_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'user_id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
    except:
        pass

    try:
        app.dynamodb.create_table(
            TableName=app.config['DYNAMODB_TABLE_ACCOUNTS'],
            KeySchema=[{'AttributeName': 'account_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'account_id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
    except:
        pass

    try:
        app.dynamodb.create_table(
            TableName=app.config['DYNAMODB_TABLE_TRANSACTIONS'],
            KeySchema=[{'AttributeName': 'transaction_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'transaction_id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
    except:
        pass

    login_manager.init_app(app)

    # Initialize notification service
    from .notifications import NotificationService
    app.notification_service = NotificationService(app.config)

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.transactions import transactions_bp
    from .routes.analytics import analytics_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(analytics_bp)

    # Root route
    @app.route('/')
    def index():
        from flask_login import current_user
        if current_user.is_authenticated:
            from flask import redirect, url_for
            return redirect(url_for('transactions.dashboard'))
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))

    return app
