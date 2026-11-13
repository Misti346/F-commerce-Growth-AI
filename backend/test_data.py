
from database import get_db_connection

connection = get_db_connection()
cursor = connection.cursor()

try:
    cursor.execute(
        "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
        ("Test Seller", "testseller@example.com", "TEST_ONLY_PASSWORD")
    )

    seller_id = cursor.lastrowid

    cursor.execute(
        """INSERT INTO customers
        (seller_id, customer_name, phone, address)
        VALUES (%s, %s, %s, %s)""",
        (seller_id, "Test Customer", "01700000000", "Dhaka, Bangladesh")
    )

    customer_id = cursor.lastrowid
    connection.commit()

    print("Seller ID:", seller_id)
    print("Customer ID:", customer_id)
    print("Test data created successfully!")

except Exception as e:
    connection.rollback()
    print("Error:", e)

finally:
    cursor.close()
    connection.close()
