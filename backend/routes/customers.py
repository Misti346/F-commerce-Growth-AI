from flask import Blueprint, request, jsonify
from database import get_db_connection

customers_bp = Blueprint("customers", __name__)


@customers_bp.route("/api/customers", methods=["POST"])
def create_customer():

    data = request.get_json()

    if data is None:
        return jsonify({
            "message": "Invalid JSON data"
        }), 400

    required_fields = ["seller_id", "customer_name"]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "message": f"{field} is required"
            }), 400

    connection = get_db_connection()

    if not connection:
        return jsonify({
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:
        cursor = connection.cursor()

        query = """
            INSERT INTO customers
            (seller_id, customer_name, phone, address)
            VALUES (%s, %s, %s, %s)
        """

        values = (
            data["seller_id"],
            data["customer_name"],
            data.get("phone"),
            data.get("address")
        )

        cursor.execute(query, values)
        connection.commit()

        return jsonify({
            "message": "Customer created successfully!",
            "customer_id": cursor.lastrowid,
            "status": "Success"
        }), 201

    except Exception as e:
        connection.rollback()

        return jsonify({
            "message": "Failed to create customer",
            "error": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()

        connection.close()