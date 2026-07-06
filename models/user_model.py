import mysql.connector
from models.db import get_connection
from config import STARTING_BALANCE


def create_user(name, email, password_hash, phone=None):
    """
    Insert a new user, auto-create an empty portfolio,
    and optionally store their phone number in user_phone.
    Returns the new user_id, or None if email already exists.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Insert user
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, balance) VALUES (%s, %s, %s, %s)",
            (name, email, password_hash, STARTING_BALANCE)
        )
        user_id = cursor.lastrowid

        # Auto-create portfolio
        cursor.execute(
            "INSERT INTO portfolio (user_id, total_invested, avg_buy_price) VALUES (%s, 0.00, 0.00)",
            (user_id,)
        )
        conn.commit()

        # Store phone number if provided
        if phone:
            cursor.execute(
                "INSERT INTO user_phone (user_id, phone_num) VALUES (%s, %s)",
                (user_id, phone)
            )
            conn.commit()

        return user_id
    except mysql.connector.IntegrityError:
        # Duplicate email
        return None
    finally:
        cursor.close()
        conn.close()


def get_user_by_email(email):
    """Fetch a user row by email for login verification."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def get_user_by_id(user_id):
    """Fetch user profile and current balance."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT user_id, name, email, balance, created_at FROM users WHERE user_id = %s",
            (user_id,)
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def update_balance(user_id, new_balance):
    """Update a user's cash balance."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET balance = %s WHERE user_id = %s", (new_balance, user_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
