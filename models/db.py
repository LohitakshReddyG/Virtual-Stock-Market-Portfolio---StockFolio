import mysql.connector
from config import DB_CONFIG

def get_connection():
    """Returns a new MySQL connection from config."""
    return mysql.connector.connect(**DB_CONFIG)
