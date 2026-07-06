# Virtual Stock Market Portfolio Manager

A full-stack DBMS project built with **MySQL + Flask + HTML/CSS/JS**.

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Database | MySQL 8.0 (`stockdbms`) |
| Backend | Python Flask (REST API, MVC pattern) |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Live Prices | `yfinance` (Yahoo Finance) |
| Auth | `bcrypt` password hashing |

## Features
- User registration & login with secure (bcrypt) hashed passwords
- **Phone number** collected at registration and stored in `user_phone` table
- **Add Funds** — deposit money to your account anytime from the dashboard
- Live stock prices fetched from Yahoo Finance on every market page load
- Buy & Sell stocks with real-time balance deduction/credit
- Portfolio tracker with P&L (profit & loss) per holding
- Full transaction history (BUY/SELL log with date & time)
- Price history recorded per stock on every refresh

## Project Structure
```
dbms_v2/
├── app.py                        # Flask entry point & blueprint registration
├── config.py                     # DB config & constants
├── requirements.txt              # Python dependencies
├── schema.sql                    # MySQL schema (run once to set up DB)
├── seed.sql                      # Seed 10 default stocks
├── models/
│   ├── db.py                     # MySQL connection helper
│   ├── user_model.py             # User CRUD + balance update
│   ├── stock_model.py            # Stock queries + price update
│   ├── portfolio_model.py        # Holdings & portfolio queries
│   └── transaction_model.py      # Transaction logging & history
├── services/
│   └── stock_price_service.py    # yfinance live-price fetcher
├── controllers/
│   ├── auth_controller.py        # /api/register, /api/login, /api/deposit
│   ├── stock_controller.py       # /api/stocks
│   ├── portfolio_controller.py   # /api/portfolio, /api/buy, /api/sell
│   └── transaction_controller.py # /api/transactions
├── templates/
│   └── index.html                # Single-page app template
└── static/
    ├── css/style.css
    └── js/app.js
```

## Setup Instructions

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create the MySQL Database
Run the schema using MySQL Workbench, or via CLI on Windows:
```powershell
Get-Content schema.sql | & "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p
Get-Content seed.sql  | & "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p
```
This creates the `stockdbms` database with all tables and seeds 10 stocks.

### 3. Configure Database Credentials
Edit `config.py`:
```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_password",
    "database": "stockdbms",
}
```

### 4. Run the App
```bash
python app.py
```
Open browser: **http://localhost:5000**

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register` | Register new user with name, phone, email & password |
| POST | `/api/login` | Login with email & password |
| GET  | `/api/user/<id>` | Get user profile & balance |
| POST | `/api/user/<id>/deposit` | Add funds to balance |
| GET  | `/api/stocks` | All stocks with live prices |
| GET  | `/api/stocks/<id>` | Stock detail + price history |
| GET  | `/api/portfolio/<user_id>` | Holdings + P&L |
| POST | `/api/buy` | Buy shares |
| POST | `/api/sell` | Sell shares |
| GET  | `/api/transactions/<user_id>` | Full transaction history |

## Database Tables

| Table | Purpose |
|-------|---------|
| `users` | User accounts, hashed passwords, cash balance |
| `user_phone` | Phone number(s) per user (collected at registration) |
| `stocks` | Stock listings with live price & last updated timestamp |
| `price_history` | Historical prices recorded on each refresh |
| `portfolio` | One portfolio per user (aggregate stats) |
| `portfolio_stock` | Per-stock holdings (shares, avg buy price, invested amount) |
| `transactions` | All BUY/SELL records with price, qty, date & time |

## Business Rules
- New users start with **₹0** balance — funds must be added manually via **Add Funds**
- **Phone number is required** at registration (7–15 digits, stored in `user_phone`)
- Maximum deposit per transaction: **₹10,00,000**
- Cannot buy if cash balance is insufficient
- Cannot sell more shares than currently owned
- Every trade is logged to the `transactions` table
- Stock prices are fetched live from Yahoo Finance on every market page load