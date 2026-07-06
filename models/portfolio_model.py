from models.db import get_connection


def get_portfolio(user_id):
    """
    Returns portfolio summary with each holding:
    - stock info, shares_owned, avg_buy_price, total_invested per stock
    - current_price from stocks table
    - current_value = shares * current_price
    - profit_loss = current_value - total_invested
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Get portfolio_id
        cursor.execute("SELECT portfolio_id, total_invested FROM portfolio WHERE user_id = %s", (user_id,))
        portfolio = cursor.fetchone()
        if not portfolio:
            return None

        pid = portfolio["portfolio_id"]

        # Get each holding
        cursor.execute(
            """
            SELECT
                ps.stock_id,
                s.stock_name,
                s.company_name,
                s.sector,
                s.current_price,
                ps.shares_owned,
                ps.avg_buy_price,
                ps.total_invested,
                (ps.shares_owned * s.current_price) AS current_value,
                ((ps.shares_owned * s.current_price) - ps.total_invested) AS profit_loss
            FROM portfolio_stock ps
            JOIN stocks s ON ps.stock_id = s.stock_id
            WHERE ps.portfolio_id = %s AND ps.shares_owned > 0
            ORDER BY s.stock_name
            """,
            (pid,)
        )
        holdings = cursor.fetchall()

        # Calculate overall portfolio metrics
        total_current_value = sum(float(h["current_value"]) for h in holdings)
        total_invested = float(portfolio["total_invested"])
        total_pl = total_current_value - total_invested

        return {
            "portfolio_id": pid,
            "total_invested": total_invested,
            "total_current_value": round(total_current_value, 2),
            "total_profit_loss": round(total_pl, 2),
            "holdings": holdings
        }
    finally:
        cursor.close()
        conn.close()


def buy_stock(user_id, stock_id, quantity, price_per_share):
    """
    Buy logic:
    1. Deduct balance from users
    2. Insert or update portfolio_stock (shares_owned, avg_buy_price, total_invested)
    3. Update portfolio.total_invested
    Returns True on success, raises ValueError on insufficient funds.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        total_cost = round(quantity * price_per_share, 2)

        # Check user balance
        cursor.execute("SELECT balance FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        if not user or float(user["balance"]) < total_cost:
            raise ValueError("Insufficient balance")

        # Get portfolio_id
        cursor.execute("SELECT portfolio_id FROM portfolio WHERE user_id = %s", (user_id,))
        port = cursor.fetchone()
        pid = port["portfolio_id"]

        # Check if stock already in portfolio
        cursor.execute(
            "SELECT shares_owned, avg_buy_price, total_invested FROM portfolio_stock WHERE portfolio_id = %s AND stock_id = %s",
            (pid, stock_id)
        )
        holding = cursor.fetchone()

        conn2 = get_connection()  # Use separate connection for writes
        w_cursor = conn2.cursor()
        try:
            if holding:
                old_shares = int(holding["shares_owned"])
                old_avg = float(holding["avg_buy_price"])
                old_total = float(holding["total_invested"])
                new_shares = old_shares + quantity
                new_total = old_total + total_cost
                new_avg = new_total / new_shares
                w_cursor.execute(
                    """UPDATE portfolio_stock
                       SET shares_owned = %s, avg_buy_price = %s, total_invested = %s
                       WHERE portfolio_id = %s AND stock_id = %s""",
                    (new_shares, round(new_avg, 2), round(new_total, 2), pid, stock_id)
                )
            else:
                w_cursor.execute(
                    """INSERT INTO portfolio_stock (portfolio_id, stock_id, shares_owned, avg_buy_price, total_invested)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (pid, stock_id, quantity, round(price_per_share, 2), round(total_cost, 2))
                )

            # Update portfolio total_invested
            w_cursor.execute(
                "UPDATE portfolio SET total_invested = total_invested + %s WHERE portfolio_id = %s",
                (total_cost, pid)
            )

            # Deduct user balance
            w_cursor.execute(
                "UPDATE users SET balance = balance - %s WHERE user_id = %s",
                (total_cost, user_id)
            )

            conn2.commit()
        finally:
            w_cursor.close()
            conn2.close()

        return True
    finally:
        cursor.close()
        conn.close()


def sell_stock(user_id, stock_id, quantity, price_per_share):
    """
    Sell logic:
    1. Validate sufficient shares
    2. Update shares_owned in portfolio_stock
    3. Update portfolio.total_invested proportionally
    4. Credit user balance
    Returns True on success, raises ValueError on insufficient shares.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Get portfolio_id
        cursor.execute("SELECT portfolio_id FROM portfolio WHERE user_id = %s", (user_id,))
        port = cursor.fetchone()
        pid = port["portfolio_id"]

        # Get current holding
        cursor.execute(
            "SELECT shares_owned, avg_buy_price, total_invested FROM portfolio_stock WHERE portfolio_id = %s AND stock_id = %s",
            (pid, stock_id)
        )
        holding = cursor.fetchone()
        if not holding or int(holding["shares_owned"]) < quantity:
            raise ValueError("Insufficient shares to sell")

        old_shares = int(holding["shares_owned"])
        old_total = float(holding["total_invested"])
        old_avg = float(holding["avg_buy_price"])
        total_sale = round(quantity * price_per_share, 2)
        cost_basis_sold = round(old_avg * quantity, 2)
        new_shares = old_shares - quantity
        new_total = max(0, old_total - cost_basis_sold)

        conn2 = get_connection()
        w_cursor = conn2.cursor()
        try:
            w_cursor.execute(
                "UPDATE portfolio_stock SET shares_owned = %s, total_invested = %s WHERE portfolio_id = %s AND stock_id = %s",
                (new_shares, round(new_total, 2), pid, stock_id)
            )
            # Update portfolio total_invested
            w_cursor.execute(
                "UPDATE portfolio SET total_invested = total_invested - %s WHERE portfolio_id = %s",
                (round(cost_basis_sold, 2), pid)
            )
            # Credit user balance
            w_cursor.execute(
                "UPDATE users SET balance = balance + %s WHERE user_id = %s",
                (total_sale, user_id)
            )
            conn2.commit()
        finally:
            w_cursor.close()
            conn2.close()

        return True
    finally:
        cursor.close()
        conn.close()
