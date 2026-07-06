from models.db import get_connection


def get_all_stocks():
    """Return all stocks with current price."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT stock_id, stock_name, company_name, sector, current_price, last_updated FROM stocks ORDER BY stock_name"
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_stock_by_id(stock_id):
    """Return a single stock by ID."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT stock_id, stock_name, company_name, sector, current_price, last_updated FROM stocks WHERE stock_id = %s",
            (stock_id,)
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def get_stock_price(stock_id):
    """Return just the current price of a stock."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT current_price FROM stocks WHERE stock_id = %s", (stock_id,))
        row = cursor.fetchone()
        return float(row[0]) if row else None
    finally:
        cursor.close()
        conn.close()


def update_stock_price(stock_id, new_price):
    """
    Update current_price in stocks table and insert a record into price_history.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE stocks SET current_price = %s WHERE stock_id = %s",
            (new_price, stock_id)
        )
        cursor.execute(
            "INSERT INTO price_history (stock_id, price) VALUES (%s, %s)",
            (stock_id, new_price)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def get_price_history(stock_id, limit=30):
    """Return the last N price history records for a stock."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT price, recorded_at
            FROM price_history
            WHERE stock_id = %s
            ORDER BY recorded_at DESC
            LIMIT %s
            """,
            (stock_id, limit)
        )
        rows = cursor.fetchall()
        # Reverse so chart shows oldest → newest
        return list(reversed(rows))
    finally:
        cursor.close()
        conn.close()
