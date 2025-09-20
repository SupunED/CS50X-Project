# FinTrack: Personal Finance Management System

**FinTrack** is a web-based personal finance management application built using **Flask** and **SQLite**. It allows users to track income, expenses, and cash balance while providing visual insights through charts. The system is designed to help users manage their finances efficiently and make informed spending decisions.

---

## Features

- **User Authentication**
  - Register new users
  - Secure login with hashed passwords
  - Logout functionality

- **Cash Balance Tracking**
  - Automatically updates cash balance after each transaction
  - Displays current cash balance on the dashboard

- **Transaction Management**
  - Add new transactions (Income or Expense)
  - Record transaction amount, description, category, and date
  - Input validation for all fields
  - Transaction timestamp automatically recorded

- **Transaction History**
  - View a list of all transactions in a responsive table
  - Transaction timestamps converted to IST (+05:30)
  - Color-coded transaction type (green for income, red for expense)

- **Overview Dashboard**
  - Pie chart displaying total income vs. total expense
  - Cash balance displayed above the chart
  - Bootstrap-styled responsive interface

---

## Database Schema

**Users Table**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    cash REAL DEFAULT 0
);
```

**Transactions Table**
```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type TEXT CHECK(type IN ('income','expense')) NOT NULL,
    amount REAL NOT NULL,
    description TEXT NOT NULL,
    date TEXT NOT NULL,
    category TEXT,
    datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
## Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/FinTrack.git
cd FinTrack
```
2. Create a virtual environment and activate it
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```
3. Install dependencies
```bash
pip install -r requirements.txt
```
4. Run the application
```bash
python app.py
```
5. Access the app
```bash
http://127.0.0.1:5000/
```

## Dependencies

- Python 3.10+
- Flask
- Flask-Session
- Werkzeug
- CS50 Library (for SQLite integration)
- Chart.js (for frontend visualizations)
- Bootstrap 5 (for styling)


## Usage

- Register a new account.
- Log in with your credentials.
- Add transactions via the form on the dashboard.
- View transaction history in the transactions page.
- Monitor income vs expense using the overview dashboard.
