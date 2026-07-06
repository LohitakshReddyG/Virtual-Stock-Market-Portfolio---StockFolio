from flask import Blueprint, request, jsonify
from models.portfolio_model import get_portfolio, buy_stock, sell_stock
from models.stock_model import get_stock_by_id, get_stock_price
from models.transaction_model import log_transaction
from services.stock_price_service import fetch_live_price

portfolio_bp = Blueprint("portfolio", __name__)


@portfolio_bp.route("/api/portfolio/<int:user_id>", methods=["GET"])
def view_portfolio(user_id):
    """Return full portfolio with holdings, current value, and P&L."""
    portfolio = get_portfolio(user_id)
    if not portfolio:
        return jsonify({"error": "Portfolio not found"}), 404

    # Serialize holdings
    holdings = []
    for h in portfolio["holdings"]:
        holdings.append({
            "stock_id": h["stock_id"],
            "stock_name": h["stock_name"],
            "company_name": h["company_name"],
            "sector": h["sector"],
            "shares_owned": int(h["shares_owned"]),
            "avg_buy_price": float(h["avg_buy_price"]),
            "total_invested": float(h["total_invested"]),
            "current_price": float(h["current_price"]),
            "current_value": round(float(h["current_value"]), 2),
            "profit_loss": round(float(h["profit_loss"]), 2),
        })

    return jsonify({
        "portfolio_id": portfolio["portfolio_id"],
        "total_invested": portfolio["total_invested"],
        "total_current_value": portfolio["total_current_value"],
        "total_profit_loss": portfolio["total_profit_loss"],
        "holdings": holdings
    }), 200


@portfolio_bp.route("/api/buy", methods=["POST"])
def buy():
    """
    Buy shares.
    Body: { user_id, stock_id, quantity }
    Fetches live price first, then executes buy.
    """
    data = request.get_json()
    user_id = data.get("user_id")
    stock_id = data.get("stock_id")
    quantity = data.get("quantity")

    if not user_id or not stock_id or not quantity:
        return jsonify({"error": "user_id, stock_id, and quantity are required"}), 400

    quantity = int(quantity)
    if quantity <= 0:
        return jsonify({"error": "Quantity must be greater than 0"}), 400

    # Fetch stock info
    stock = get_stock_by_id(stock_id)
    if not stock:
        return jsonify({"error": "Stock not found"}), 404

    # Fetch live price
    live_price = fetch_live_price(stock["stock_name"])
    price = live_price if live_price else float(stock["current_price"])

    try:
        buy_stock(user_id, stock_id, quantity, price)
        log_transaction(user_id, stock_id, quantity, price, "BUY")
        return jsonify({
            "message": f"Successfully bought {quantity} share(s) of {stock['stock_name']}",
            "quantity": quantity,
            "price_per_share": price,
            "total_cost": round(quantity * price, 2)
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@portfolio_bp.route("/api/sell", methods=["POST"])
def sell():
    """
    Sell shares.
    Body: { user_id, stock_id, quantity }
    Fetches live price first, then executes sell.
    """
    data = request.get_json()
    user_id = data.get("user_id")
    stock_id = data.get("stock_id")
    quantity = data.get("quantity")

    if not user_id or not stock_id or not quantity:
        return jsonify({"error": "user_id, stock_id, and quantity are required"}), 400

    quantity = int(quantity)
    if quantity <= 0:
        return jsonify({"error": "Quantity must be greater than 0"}), 400

    stock = get_stock_by_id(stock_id)
    if not stock:
        return jsonify({"error": "Stock not found"}), 404

    # Fetch live price
    live_price = fetch_live_price(stock["stock_name"])
    price = live_price if live_price else float(stock["current_price"])

    try:
        sell_stock(user_id, stock_id, quantity, price)
        log_transaction(user_id, stock_id, quantity, price, "SELL")
        return jsonify({
            "message": f"Successfully sold {quantity} share(s) of {stock['stock_name']}",
            "quantity": quantity,
            "price_per_share": price,
            "total_received": round(quantity * price, 2)
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
