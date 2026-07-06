import yfinance as yf
from models.stock_model import get_all_stocks, update_stock_price


def fetch_live_price(ticker_symbol):
    """
    Fetch the current market price for a ticker using yfinance.
    Returns float price or None if fetching fails.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.fast_info
        price = info.last_price
        if price and price > 0:
            return round(float(price), 2)
        return None
    except Exception as e:
        print(f"[yfinance] Error fetching {ticker_symbol}: {e}")
        return None


def refresh_all_stock_prices():
    """
    Loop through all stocks in DB, fetch live price from Yahoo Finance,
    and update both the stocks table and price_history table.
    Returns a dict of {stock_name: new_price}.
    """
    stocks = get_all_stocks()
    results = {}
    for stock in stocks:
        ticker = stock["stock_name"]   # e.g. 'AAPL', 'RELIANCE.NS'
        price = fetch_live_price(ticker)
        if price is not None:
            update_stock_price(stock["stock_id"], price)
            results[ticker] = price
            print(f"[Price Update] {ticker}: ₹{price}")
        else:
            results[ticker] = stock["current_price"]
            print(f"[Price Update] {ticker}: fetch failed, keeping existing price")
    return results
