from flask import Flask, render_template
from flask_cors import CORS

from controllers.auth_controller import auth_bp
from controllers.stock_controller import stock_bp
from controllers.portfolio_controller import portfolio_bp
from controllers.transaction_controller import transaction_bp
from config import SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY
CORS(app)

# Register all blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(stock_bp)
app.register_blueprint(portfolio_bp)
app.register_blueprint(transaction_bp)


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    print("="*50)
    print(" Virtual Stock Market Portfolio Manager")
    print(" Running at: http://localhost:5000")
    print("="*50)
    app.run(debug=True, port=5000)
