from flask import Blueprint, request, jsonify
import bcrypt
from models.user_model import create_user, get_user_by_email, get_user_by_id, update_balance

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    phone = data.get("phone", "").strip()

    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password are required"}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    if not phone:
        return jsonify({"error": "Phone number is required"}), 400

    # Basic phone validation: digits only, 7-15 chars
    if not phone.replace("+", "").replace("-", "").replace(" ", "").isdigit() or not (7 <= len(phone.replace(" ", "")) <= 15):
        return jsonify({"error": "Enter a valid phone number (7-15 digits)"}), 400

    # Hash password
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    user_id = create_user(name, email, hashed, phone)
    if user_id is None:
        return jsonify({"error": "Email already registered"}), 409

    user = get_user_by_id(user_id)
    return jsonify({
        "message": "Registration successful",
        "user": {
            "user_id": user["user_id"],
            "name": user["name"],
            "email": user["email"],
            "balance": float(user["balance"])
        }
    }), 201


@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = get_user_by_email(email)
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    if not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        return jsonify({"error": "Invalid email or password"}), 401

    return jsonify({
        "message": "Login successful",
        "user": {
            "user_id": user["user_id"],
            "name": user["name"],
            "email": user["email"],
            "balance": float(user["balance"])
        }
    }), 200


@auth_bp.route("/api/user/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "user_id": user["user_id"],
        "name": user["name"],
        "email": user["email"],
        "balance": float(user["balance"]),
        "created_at": str(user["created_at"])
    }), 200


@auth_bp.route("/api/user/<int:user_id>/deposit", methods=["POST"])
def deposit_funds(user_id):
    """Add funds to a user's cash balance."""
    data = request.get_json()
    try:
        amount = float(data.get("amount", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid amount"}), 400

    if amount <= 0:
        return jsonify({"error": "Deposit amount must be greater than ₹0"}), 400
    if amount > 1_000_000:
        return jsonify({"error": "Maximum deposit per transaction is ₹10,00,000"}), 400

    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    new_balance = float(user["balance"]) + amount
    update_balance(user_id, new_balance)

    return jsonify({
        "message": f"₹{amount:,.2f} added successfully",
        "balance": round(new_balance, 2)
    }), 200
