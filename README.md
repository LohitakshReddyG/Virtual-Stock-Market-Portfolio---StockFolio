# Virtual-Stock-Market-Portfolio---StockFolio
A web-based virtual stock market simulator for managing mock portfolios, tracking stock prices, and practicing trading strategies risk-free.
markdown


# 📈 StockFolio: Virtual Stock Market Simulator

**StockFolio** is a web-based virtual stock market simulator designed to help users practice trading without any financial risk. Built with Python and Flask, this platform allows users to create an account, manage a mock portfolio, simulate buying and selling stocks, and track transaction history in a risk-free sandbox environment.
## ✨ Features
* **User Authentication:** Secure login and registration system.
* **Portfolio Management:** View current holdings, total portfolio value, and available cash balance.
* **Simulated Trading:** Buy and sell virtual stocks with real-time or mocked market data.
* **Transaction History:** Keep a detailed log of every trade made (Buy/Sell, quantity, price, and date).
* **Responsive Dashboard:** A clean, easy-to-use web interface built with HTML, CSS, and JavaScript.
## 🛠️ Technology Stack
* **Backend:** Python, Flask
* **Frontend:** HTML5, Vanilla CSS, JavaScript
* **Database:** SQLite (via standard `schema.sql`)
* **Routing & Controllers:** Flask Blueprints for modular architecture
## 🚀 Getting Started
Follow these instructions to get a copy of the project up and running on your local machine.
### Prerequisites
* Python 3.8+
* `pip` (Python package installer)
### Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/LohitakshReddyG/Virtual-Stock-Market-Portfolio---StockFolio.git
   cd Virtual-Stock-Market-Portfolio---StockFolio
Set up a Virtual Environment (Recommended):

bash


python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
Install Dependencies:

bash


pip install -r requirements.txt
Initialize the Database: (Instructions depend on your exact setup, usually it involves running your seed script)

bash


sqlite3 database.db < schema.sql
sqlite3 database.db < seed.sql
Run the Application:

bash


python app.py
The application will start running at http://localhost:5000/.

📁 Project Structure


├── controllers/          # Flask Blueprints (auth, stock, portfolio, transactions)
├── models/               # Database interaction logic
├── services/             # Core business logic and external API calls
├── static/               # CSS, JS, and Images
├── templates/            # HTML Views
├── app.py                # Main application entry point
├── config.py             # Configuration settings and Secret Keys
├── schema.sql            # Database schema definitions
└── requirements.txt      # Python dependencies

🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

📝 License
This project is open source.
