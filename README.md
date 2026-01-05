# AgriBank Management Platform

![AgriBank Screenshot](https://i.ibb.co/Pz3KZtCk/Screenshot-2026-01-05-142055.png)

A comprehensive banking management system built specifically for agricultural development in Ghana. AgriBank provides secure, accessible financial services tailored for farmers, agribusinesses, and agricultural stakeholders.

## 🌾 About AgriBank

AgricBank is a leading financial institution committed to advancing agricultural development through comprehensive banking services. We partner with farmers and agribusinesses to provide accessible credit, secure savings solutions, and investment opportunities that drive productivity and sustainability in the agricultural sector.

## 🔗 Links

- **Live Demo**: https://bank-account-management-system-p4m4.onrender.com/login
- **API Documentation (Swagger)**: https://agribank.onrender.com/docs#/

## ✨ Features

### 🔐 User Management
- Secure user registration and authentication
- JWT-based token authentication
- User profile management
- Password hashing with bcrypt

### 💳 Account Management
- **Savings Accounts**: Minimum balance requirements, interest calculation
- **Current Accounts**: Overdraft facilities, flexible transactions
- **Fixed Deposit Accounts**: Maturity calculations with compound interest
- Ghanaian account numbering (GH + 8 digits)
- Account freezing/unfreezing capabilities
- Account closure functionality

### 💰 Transaction Processing
- Deposits and withdrawals
- Inter-account transfers
- Transaction history with pagination
- Real-time balance updates
- Comprehensive transaction logging

### 📊 Financial Services
- Monthly interest calculation for savings accounts (3.5% APR)
- Portfolio summary and analytics
- Balance inquiries
- Transaction statements

## 🛠 Technology Stack

- **Backend Framework**: FastAPI
- **Database**: MongoDB
- **Authentication**: JWT (JSON Web Tokens)
- **Validation**: Pydantic
- **Password Hashing**: bcrypt
- **ASGI Server**: Uvicorn
- **Language**: Python 3.8+

## 📋 Prerequisites

- Python 3.8 or higher
- MongoDB Atlas account or local MongoDB instance
- Git

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/p-mensah/agribank.git
cd agribank
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the root directory:
```env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/agribank?retryWrites=true&w=majority
JWT_SECRET_KEY=your_super_secret_jwt_key_here
```

### 5. Run the Application
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

### Authentication Endpoints

#### POST `/users/signup`
Register a new user account.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "phone": 233501234567,
  "address": "Accra, Ghana"
}
```

#### POST `/users/login`
Authenticate user and receive access token.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

#### GET `/users/me`
Get current user profile (requires authentication).

### Account Management Endpoints

#### POST `/accounts`
Create a new bank account.

**Request Body:**
```json
{
  "type": "SAVINGS",
  "holder_name": "John Doe",
  "initial_balance": 200.00,
  "overdraft_limit": 1000.00,
  "tenure_months": 12
}
```

**Supported Account Types:**
- `SAVINGS`: Minimum balance GH¢100, 3.5% interest
- `CURRENT`: Overdraft facility up to GH¢5,000
- `FIXED_DEPOSIT`: Term deposits with compound interest

#### GET `/accounts`
List all user accounts.

#### GET `/accounts/{id}`
Get specific account details.

#### GET `/accounts/{id}/balance`
Check account balance.

#### DELETE `/accounts/{id}`
Close an account (balance must be zero).

#### PATCH `/accounts/{id}/freeze`
Freeze or unfreeze an account.

#### POST `/accounts/{id}/calculate-interest`
Calculate monthly interest for savings accounts.

#### GET `/accounts/portfolio/summary`
Get portfolio overview.

### Transaction Endpoints

#### POST `/transactions/deposit`
Deposit funds into an account.

**Parameters:**
- `account_number`: Target account number
- `amount`: Deposit amount

#### POST `/transactions/withdraw`
Withdraw funds from an account.

**Parameters:**
- `account_number`: Source account number
- `amount`: Withdrawal amount

#### POST `/transactions/transfer`
Transfer funds between accounts.

**Parameters:**
- `from_account`: Source account number
- `to_account_number`: Destination account number
- `amount`: Transfer amount

#### GET `/transactions/{account_number}/history`
Get transaction history for an account.

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 50)

## 🧪 Testing

### Run API Tests
```bash
python test_api.py
```

### Manual Testing with cURL

1. **Register a new user:**
```bash
curl -X POST "http://localhost:8000/users/signup" \
  -d "name=Test User" \
  -d "email=test@example.com" \
  -d "password=password123" \
  -d "phone=233501234567" \
  -d "address=Accra, Ghana"
```

2. **Login and get token:**
```bash
curl -X POST "http://localhost:8000/users/login" \
  -d "email=test@example.com" \
  -d "password=password123"
```

3. **Create a savings account:**
```bash
curl -X POST "http://localhost:8000/accounts" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "SAVINGS",
    "holder_name": "Test User",
    "initial_balance": 200.00
  }'
```

## 📁 Project Structure

```
agribank/
├── main.py                 # FastAPI application entry point
├── db.py                   # MongoDB connection and collections
├── utils.py               # Utility functions
├── requirements.txt       # Python dependencies
├── test_api.py           # API testing script
├── .env                  # Environment variables (create this)
├── dependencies/
│   └── authn.py          # JWT authentication middleware
└── router/
    ├── users.py          # User management endpoints
    ├── accounts.py       # Account management endpoints
    ├── transactions.py   # Transaction processing endpoints
    ├── account_type.py   # Account data models
    └── transaction_schemas.py  # Transaction data models
```

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt encryption for passwords
- **Input Validation**: Pydantic models for data validation
- **CORS Protection**: Configured CORS middleware
- **Account Ownership**: Users can only access their own accounts

## 🌍 Business Rules

### Account Types & Requirements

#### Savings Accounts
- Minimum opening balance: GH¢100
- Minimum maintenance balance: GH¢100
- Interest rate: 3.5% per annum (compounded monthly)
- No overdraft facility

#### Current Accounts
- No minimum balance requirement
- Overdraft limit: Up to GH¢5,000
- No interest on positive balances
- Flexible transaction capabilities

#### Fixed Deposit Accounts
- Minimum tenure: 1 month
- Maximum tenure: 120 months
- Interest rate: 5.5% per annum (compounded monthly)
- Early withdrawal restrictions

### Transaction Limits
- Deposits: No upper limit
- Withdrawals: Subject to account balance and overdraft limits
- Transfers: Subject to available balance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support and inquiries:
- Email: support@agribank.com
- Phone: +233 30 123 4567
- Address: Accra, Ghana

## 🔄 API Version

**Current Version:** v1.0.0

The API follows RESTful conventions and uses standard HTTP status codes. All endpoints return JSON responses.

---

**Built with ❤️ for Ghana's agricultural community**
