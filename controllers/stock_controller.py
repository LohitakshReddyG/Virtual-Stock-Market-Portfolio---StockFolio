from flask import Blueprint, jsonify
from models.stock_model import get_all_stocks, get_stock_by_id, get_price_history
from services.stock_price_service import refresh_all_stock_prices

stock_bp = Blueprint("stocks", __name__)


@stock_bp.route("/api/stocks", methods=["GET"])
def list_stocks():
    """
    Returns all stocks with live prices from Yahoo Finance.
    Triggers a price refresh on every call.
    """
    try:
        refresh_all_stock_prices()
    except Exception as e:
        print(f"[Stock Price Refresh Error] {e}")

    stocks = get_all_stocks()
    result = []
    for s in stocks:
        result.append({
            "stock_id": s["stock_id"],
            "stock_name": s["stock_name"],
            "company_name": s["company_name"],
            "sector": s["sector"],
            "current_price": float(s["current_price"]),
            "last_updated": str(s["last_updated"])
        })
    return jsonify(result), 200


@stock_bp.route("/api/stocks/<int:stock_id>", methods=["GET"])
def get_stock(stock_id):
    """Returns a single stock's info plus price history."""
    stock = get_stock_by_id(stock_id)
    if not stock:
        return jsonify({"error": "Stock not found"}), 404

    history = get_price_history(stock_id, limit=30)
    history_data = [
        {"price": float(h["price"]), "recorded_at": str(h["recorded_at"])}
        for h in history
    ]

    return jsonify({
        "stock_id": stock["stock_id"],
        "stock_name": stock["stock_name"],
        "company_name": stock["company_name"],
        "sector": stock["sector"],
        "current_price": float(stock["current_price"]),
        "last_updated": str(stock["last_updated"]),
        "price_history": history_data
    }), 200
