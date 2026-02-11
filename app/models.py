from flask_login import UserMixin
import boto3
import uuid
from datetime import datetime, timezone
from bcrypt import hashpw, checkpw, gensalt
from decimal import Decimal


class User(UserMixin):
    def __init__(self, user_id, email, password_hash, name, created_at, phone=None):
        self.id = user_id
        self.user_id = user_id
        self.email = email
        self.password_hash = password_hash
        self.name = name
        self.created_at = created_at
        self.phone = phone

    def check_password(self, password):
        """Check if the provided password matches the stored hash"""
        return checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    @staticmethod
    def create(email, password, name):
        """Create a new user"""
        from flask import current_app
        user_id = str(uuid.uuid4())
        password_hash = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')
        created_at = datetime.now(timezone.utc).isoformat()

        table = current_app.dynamodb.Table(current_app.config['DYNAMODB_TABLE_USERS'])
        table.put_item(Item={
            'user_id': user_id,
            'email': email,
            'password_hash': password_hash,
            'name': name,
            'created_at': created_at
        })
        
        return User(user_id, email, password_hash, name, created_at)

    @staticmethod
    def get(user_id):
        from flask import current_app
        table = current_app.dynamodb.Table(current_app.config['DYNAMODB_TABLE_USERS'])
        response = table.get_item(Key={'user_id': user_id})
        if 'Item' in response:
            item = response['Item']
            return User(
                item['user_id'],
                item['email'],
                item['password_hash'],
                item['name'],
                item['created_at'],
                item.get('phone')
            )
        return None

    @staticmethod
    def get_by_email(email):
        from flask import current_app
        table = current_app.dynamodb.Table(current_app.config['DYNAMODB_TABLE_USERS'])
        response = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('email').eq(email)
        )
        if response['Items']:
            item = response['Items'][0]
            return User(
                item['user_id'],
                item['email'],
                item['password_hash'],
                item['name'],
                item['created_at']
            )
        return None


class Account:
    def __init__(self, account_id, user_id, balance, created_at):
        self.account_id = account_id
        self.user_id = user_id
        self.balance = balance
        self.created_at = created_at

    @staticmethod
    def create(user_id):
        """Create a new account for a user"""
        from flask import current_app
        account_id = str(uuid.uuid4())
        balance = Decimal('0.0')
        created_at = datetime.now(timezone.utc).isoformat()

        table = current_app.dynamodb.Table(current_app.config['DYNAMODB_TABLE_ACCOUNTS'])
        table.put_item(Item={
            'account_id': account_id,
            'user_id': user_id,
            'balance': balance,
            'created_at': created_at
        })

        return Account(account_id, user_id, float(balance), created_at)

    @staticmethod
    def get(user_id):
        """Get account for a user"""
        from flask import current_app
        table = current_app.dynamodb.Table(current_app.config['DYNAMODB_TABLE_ACCOUNTS'])
        response = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('user_id').eq(user_id)
        )
        if response['Items']:
            item = response['Items'][0]
            return Account(
                item['account_id'],
                item['user_id'],
                float(item['balance']),
                item['created_at']
            )
        return None

    @staticmethod
    def get_by_account_id(account_id):
        """Get account by account_id"""
        from flask import current_app
        table = current_app.dynamodb.Table(current_app.config['DYNAMODB_TABLE_ACCOUNTS'])
        response = table.get_item(Key={'account_id': account_id})
        if 'Item' in response:
            item = response['Item']
            return Account(
                item['account_id'],
                item['user_id'],
                float(item['balance']),
                item['created_at']
            )
        return None

    def update_balance(self, amount):
        """Update account balance"""
        from flask import current_app
        self.balance += amount
        table = current_app.dynamodb.Table(current_app.config['DYNAMODB_TABLE_ACCOUNTS'])
        table.update_item(
            Key={'account_id': self.account_id},
            UpdateExpression='SET #balance = :balance',
            ExpressionAttributeNames={'#balance': 'balance'},
            ExpressionAttributeValues={':balance': Decimal(str(self.balance))}
        )


class Transaction:
    def __init__(self, transaction_id, from_account_id, to_account_id, amount, transaction_type, description, created_at):
        self.transaction_id = transaction_id
        self.from_account_id = from_account_id
        self.to_account_id = to_account_id
        self.amount = amount
        self.transaction_type = transaction_type
        self.description = description
        self.created_at = created_at

    @staticmethod
    def create(from_account_id, to_account_id, amount, transaction_type, description):
        """Create a new transaction"""
        from flask import current_app
        transaction_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()

        table = current_app.dynamodb.Table(current_app.config['DYNAMODB_TABLE_TRANSACTIONS'])
        table.put_item(Item={
            'transaction_id': transaction_id,
            'from_account_id': from_account_id,
            'to_account_id': to_account_id,
            'amount': Decimal(str(amount)),
            'transaction_type': transaction_type,
            'description': description,
            'created_at': created_at
        })

        return Transaction(transaction_id, from_account_id, to_account_id, float(amount), transaction_type, description, created_at)

    @staticmethod
    def get_transactions_for_account(account_id, limit=100):
        """Get transactions for an account"""
        from flask import current_app
        table = current_app.dynamodb.Table(current_app.config['DYNAMODB_TABLE_TRANSACTIONS'])
        
        # Query transactions where from_account_id or to_account_id matches
        response = table.scan(
            FilterExpression=(
                boto3.dynamodb.conditions.Attr('from_account_id').eq(account_id) |
                boto3.dynamodb.conditions.Attr('to_account_id').eq(account_id)
            ),
            Limit=limit
        )
        
        transactions = []
        for item in response.get('Items', []):
            transactions.append(Transaction(
                item['transaction_id'],
                item.get('from_account_id'),
                item.get('to_account_id'),
                float(item['amount']),
                item['transaction_type'],
                item['description'],
                item['created_at']
            ))
        
        return transactions
