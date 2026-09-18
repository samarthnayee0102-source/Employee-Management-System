import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG


def create_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)

        if connection.is_connected():
            print("✅ Database connected successfully!")
            return connection

    except Error as e:
        print(f"❌ Database connection failed: {e}")

    return None