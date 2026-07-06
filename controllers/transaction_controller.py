from flask import Blueprint, jsonify
from models.transaction_model import get_user_transactions

transaction_bp = Blueprint("transactions", __name__)


@transaction_bp.route("/api/transactions/<int:user_id>", methods=["GET"])
def get_transactions(user_id):
    """Return full transaction history for a user, newest first."""
    transactions = get_user_transactions(user_id, limit=100)
    result = []
    for t in transactions:
        result.append({
            "transaction_id": t["transaction_id"],
            "transaction_type": t["transaction_type"],
            "stock_name": t["stock_name"],
            "company_name": t["company_name"],
            "quantity": t["quantity"],
            "price_per_share": float(t["price_per_share"]),
            "total_amount": float(t["total_amount"]),
            "transaction_date": str(t["transaction_date"]),
            "transaction_time": str(t["transaction_time"])
        })
    return jsonify(result), 200
