# Cloud-Hosted Banking Data Analytics

A professional Flask-based banking application with AWS DynamoDB integration for real-time transaction monitoring, fraud detection, custom reporting, and regulatory compliance management.

## 🚀 Features

- **User Authentication**: Secure registration and login with encrypted passwords
- **Banking Operations**: Deposit, withdraw, and transfer funds with real-time balance updates
- **Real-time Analytics**: Live transaction monitoring with fraud detection alerts
- **Custom Reports**: Generate comprehensive financial reports in multiple formats
- **Compliance Monitoring**: Track regulatory compliance with automated alerts
- **Responsive Design**: Modern web interface that works on all devices
- **Cloud Integration**: AWS DynamoDB for scalable, secure data storage

## 🛠️ Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: AWS DynamoDB (NoSQL cloud database)
- **Authentication**: Flask-Login with bcrypt encryption
- **Frontend**: Bootstrap 5, Chart.js for data visualization
- **Cloud Services**: AWS (DynamoDB, EC2 for deployment)
- **Security**: Flask-WTF for form validation, secure session management

## 📋 Prerequisites

- Python 3.8 or higher
- Git
- AWS account (for production deployment)
- Docker (optional, for local DynamoDB testing)

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/SanjanMV/Cloud-Hosted-banking-data-analitics.git
   cd Cloud-Hosted-banking-data-analitics
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   Create a `.env` file in the project root:
   ```
   SECRET_KEY=your-secret-key-here
   AWS_REGION=us-east-1
   DYNAMODB_ENDPOINT_URL=http://localhost:8000  # For local development
   FLASK_ENV=development
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

   Visit `http://localhost:5000` in your browser.

## 📖 Usage

### Getting Started
1. **Register**: Create a new account with your details
2. **Login**: Access your secure banking dashboard
3. **Dashboard**: View account balance and recent transactions

### Banking Operations
- **Deposit**: Add funds to your account instantly
- **Withdraw**: Remove funds (subject to balance availability)
- **Transfer**: Send money to other accounts securely

### Analytics & Reports
- **Analytics Dashboard**: Monitor transaction patterns and alerts
- **Reports**: Generate detailed financial reports
- **Compliance**: Track regulatory compliance status

## 🏗️ Project Structure

```
├── app/
│   ├── __init__.py          # Flask app initialization
│   ├── models.py            # Database models
│   ├── routes/              # API endpoints
│   │   ├── auth.py          # Authentication routes
│   │   ├── transactions.py  # Banking operations
│   │   └── analytics.py     # Analytics routes
│   ├── templates/           # HTML templates
│   └── static/css/          # Stylesheets
├── config.py                # Configuration settings
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔒 Security Features

- Password encryption using bcrypt
- Secure session management
- Form validation and CSRF protection
- AWS IAM roles for database access
- Environment variable protection for secrets

## 📊 Key Scenarios

### Real-time Fraud Detection
Monitor transactions in real-time with automated alerts for suspicious activities like high-value transfers.

### Regulatory Compliance
Track compliance metrics and receive alerts when thresholds are approached, ensuring regulatory adherence.

## 🚀 Deployment

### Local Development
- Use Docker for local DynamoDB: `docker run -p 8000:8000 amazon/dynamodb-local`
- Run with `python run.py`

### Production (AWS)
1. Set up EC2 instance
2. Configure AWS credentials
3. Use production DynamoDB endpoint
4. Set up load balancer and auto-scaling
5. Enable CloudWatch monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License 

## 🙏 Acknowledgments

- Flask community for the excellent web framework
- AWS for cloud infrastructure services
- Bootstrap and Chart.js for UI components
