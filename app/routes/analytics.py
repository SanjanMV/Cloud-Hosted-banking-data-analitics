from flask import Blueprint, render_template
from flask_login import login_required, current_user
from ..models import Transaction, Account
from datetime import datetime, timedelta

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
@login_required
def dashboard():
    """
    Scenario 1: Real-time Transaction Monitoring
    Sarah, a bank's fraud detection analyst, views alerts for unusual transaction patterns.
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)

    account = Account.get(current_user.id)
    if account:
        transactions = Transaction.get_transactions_for_account(account.account_id, limit=100)
    else:
        transactions = []

    # Calculate basic metrics
    total_transactions = len(transactions)
    total_volume = sum(t.amount for t in transactions if t.transaction_type in ['deposit', 'transfer'])

    # Scenario 1: Fraud detection - flag transactions above $10,000 threshold
    suspicious_transactions = [t for t in transactions if t.amount > 10000]
    suspicious_count = len(suspicious_transactions)

    # Pass transactions to template for real-time monitoring
    return render_template('analytics.html',
                         total_transactions=total_transactions,
                         total_volume=total_volume,
                         suspicious_transactions=suspicious_count,
                         transactions=transactions)

@analytics_bp.route('/reports')
@login_required
def reports():
    """
    Scenario 2: Custom Report Generation
    John, a financial manager, prepares comprehensive quarterly reports for board meetings.
    The system processes data from DynamoDB using AWS EC2 analytics.
    """
    account = Account.get(current_user.id)
    if account:
        transactions = Transaction.get_transactions_for_account(account.account_id, limit=1000)
        total_deposits = sum(t.amount for t in transactions if t.transaction_type == 'deposit')
        total_withdrawals = sum(t.amount for t in transactions if t.transaction_type == 'withdraw')
        total_transfers = sum(t.amount for t in transactions if t.transaction_type == 'transfer')
        
        report_data = {
            'total_transactions': len(transactions),
            'total_deposits': total_deposits,
            'total_withdrawals': total_withdrawals,
            'total_transfers': total_transfers,
            'current_balance': account.balance,
            'transactions': transactions[:50]  # Show last 50 transactions
        }
    else:
        report_data = None
    
    return render_template('reports.html', report_data=report_data)

@analytics_bp.route('/compliance')
@login_required
def compliance():
    """
    Scenario 3: Regulatory Compliance Monitoring
    Lisa, a compliance officer, monitors key compliance metrics in real-time.
    She can drill down into underlying data to identify root causes and initiate corrective actions.
    """
    account = Account.get(current_user.id)
    compliance_status = "All metrics within regulatory thresholds."
    compliance_percentage = 100
    alerts = []

    if account:
        transactions = Transaction.get_transactions_for_account(account.account_id, limit=1000)

        # Scenario 3: Large transaction detection for regulatory monitoring
        large_transactions = [t for t in transactions if t.amount > 10000]
        if large_transactions:
            alerts.append(f"Large transactions detected: {len(large_transactions)} transactions over $10,000")
            compliance_percentage = 85

        # Scenario 3: Frequent small transactions (potential money laundering - AML check)
        recent_transactions = [t for t in transactions if (datetime.utcnow() - datetime.fromisoformat(t.created_at.replace('Z', '+00:00'))).days <= 7]
        if len(recent_transactions) > 50:
            alerts.append("High transaction frequency detected")
            compliance_percentage = max(compliance_percentage - 10, 70)

        # Scenario 3: Balance threshold check
        if account.balance < 0:
            alerts.append("Negative balance detected")
            compliance_percentage = 50
            compliance_status = "Critical compliance issues detected."

        if not alerts:
            alerts.append("No compliance issues detected.")
    else:
        alerts.append("No account data available.")

    return render_template('compliance.html',
                         compliance_status=compliance_status,
                         compliance_percentage=compliance_percentage,
                         alerts=alerts)
