from models.db import get_connection


def log_transaction(user_id, stock_id, quantity, price_per_share, transaction_type):
    """Insert a BUY or SELL record into the transactions table."""
    total_amount = round(quantity * price_per_share, 2)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO transactions
                (user_id, stock_id, quantity, price_per_share, total_amount, transaction_type)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (user_id, stock_id, quantity, price_per_share, total_amount, transaction_type)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def get_user_transactions(user_id, limit=50):
    """Return the last N transactions for a user, newest first."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                t.transaction_id,
                t.transaction_type,
                t.quantity,
                t.price_per_share,
                t.total_amount,
                t.transaction_date,
                t.transaction_time,
                s.stock_name,
                s.company_name
            FROM transactions t
            JOIN stocks s ON t.stock_id = s.stock_id
            WHERE t.user_id = %s
            ORDER BY t.transaction_date DESC, t.transaction_time DESC
            LIMIT %s
            """,
            (user_id, limit)
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
