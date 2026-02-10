from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import Account, Transaction, User
from ..notifications import send_transaction_notification
from datetime import datetime, timedelta

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/dashboard')
@login_required
def dashboard():
    """Real-time dashboard showing account balance and transaction monitoring"""
    account = Account.get(current_user.id)  # Assuming account_id is user_id for simplicity
    if not account:
        account = Account.create(current_user.id)
    
    transactions = Transaction.get_transactions_for_account(account.account_id)
    
    # Calculate monthly volume for the last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    monthly_transactions = []
    monthly_volume = 0
    
    for t in transactions:
        try:
            tx_date = datetime.fromisoformat(t.created_at.replace('Z', '+00:00'))
            if tx_date >= thirty_days_ago:
                monthly_transactions.append(t)
                if t.transaction_type in ['deposit', 'transfer']:
                    monthly_volume += t.amount
        except:
            # Handle any date parsing issues
            monthly_transactions.append(t)
            if t.transaction_type in['deposit', 'transfer']:
                monthly_volume += t.amount
    
    return render_template('dashboard.html', 
                         account=account, 
                         transactions=transactions,
                         monthly_volume=monthly_volume)

@transactions_bp.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        account = Account.get(current_user.id)
        if account:
            account.update_balance(amount)
            Transaction.create(None, account.account_id, amount, 'deposit', 'Deposit')

            # Send notification
            user = User.get(current_user.id)
            send_transaction_notification(
                user_email=user.email,
                user_phone=user.phone,
                transaction_type='deposit',
                amount=amount,
                balance=account.balance
            )

            flash('Deposit successful', 'success')
            return redirect(url_for('transactions.dashboard'))
    return render_template('deposit.html')

@transactions_bp.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        account = Account.get(current_user.id)
        if account and account.balance >= amount:
            account.update_balance(-amount)
            Transaction.create(account.account_id, None, amount, 'withdraw', 'Withdrawal')

            # Send notification
            user = User.get(current_user.id)
            send_transaction_notification(
                user_email=user.email,
                user_phone=user.phone,
                transaction_type='withdrawal',
                amount=amount,
                balance=account.balance
            )

            flash('Withdrawal successful', 'success')
            return redirect(url_for('transactions.dashboard'))
        flash('Insufficient funds', 'warning')
    return render_template('withdraw.html')

@transactions_bp.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    if request.method == 'POST':
        recipient_input = request.form.get('to_account_id').strip()
        amount = float(request.form.get('amount'))
        from_account = Account.get(current_user.id)

        # Try to find the recipient account
        to_account = None

        # First, try to find by account_id
        to_account = Account.get_by_account_id(recipient_input)

        # If not found by account_id, try to find by email
        if not to_account:
            recipient_user = User.get_by_email(recipient_input)
            if recipient_user:
                to_account = Account.get(recipient_user.id)

        if from_account and to_account and from_account.balance >= amount and from_account.account_id != to_account.account_id:
            from_account.update_balance(-amount)
            to_account.update_balance(amount)
            Transaction.create(from_account.account_id, to_account.account_id, amount, 'transfer', 'Transfer')

            # Send notification for the transfer
            user = User.get(current_user.id)
            send_transaction_notification(
                user_email=user.email,
                user_phone=user.phone,
                transaction_type='transfer',
                amount=amount,
                balance=from_account.balance
            )

            flash('Transfer successful', 'success')
            return redirect(url_for('transactions.dashboard'))
        elif from_account and to_account and from_account.account_id == to_account.account_id:
            flash('Cannot transfer to your own account', 'warning')
        else:
            flash('Transfer failed - please check recipient email/account ID and ensure sufficient funds', 'danger')
    return render_template('transfer.html')
