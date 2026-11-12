
import mysql.connector
from mysql.connector import Error


def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Misti346",
            database="fcommerce_growth_ai"
        )

        if connection.is_connected():
            print("MySQL Database Connected Successfully!")
            return connection

    except Error as e:
        print("Database Connection Failed:", e)
        return None
