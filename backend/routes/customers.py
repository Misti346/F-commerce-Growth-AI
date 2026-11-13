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

@customers_bp.route("/api/customers", methods=["GET"])
def get_all_customers():

    connection = get_db_connection()

    if not connection:
        return jsonify({
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT customer_id, seller_id, customer_name, phone, address, created_at
            FROM customers
        """

        cursor.execute(query)
        customers = cursor.fetchall()

        return jsonify({
            "message": "Customers retrieved successfully!",
            "total_customers": len(customers),
            "customers": customers,
            "status": "Success"
        }), 200

    except Exception as e:
        return jsonify({
            "message": "Failed to retrieve customers",
            "error": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()

        connection.close()


@customers_bp.route("/api/customers/<int:customer_id>", methods=["GET"])
def get_single_customer(customer_id):

    connection = get_db_connection()

    if not connection:
        return jsonify({
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT customer_id, seller_id, customer_name, phone, address, created_at
            FROM customers
            WHERE customer_id = %s
        """

        cursor.execute(query, (customer_id,))
        customer = cursor.fetchone()

        if not customer:
            return jsonify({
                "message": "Customer not found"
            }), 404

        return jsonify({
            "message": "Customer retrieved successfully!",
            "customer": customer,
            "status": "Success"
        }), 200

    except Exception as e:
        return jsonify({
            "message": "Failed to retrieve customer",
            "error": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()

        connection.close()
@customers_bp.route("/api/customers/<int:customer_id>", methods=["PUT"])
def update_customer(customer_id):

    data = request.get_json()

    if data is None:
        return jsonify({
            "message": "Invalid JSON data"
        }), 400

    connection = get_db_connection()

    if not connection:
        return jsonify({
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute(
            "SELECT customer_id FROM customers WHERE customer_id = %s",
            (customer_id,)
        )

        if not cursor.fetchone():
            return jsonify({
                "message": "Customer not found"
            }), 404

        allowed_fields = ["customer_name", "phone", "address"]

        update_fields = []
        values = []

        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                values.append(data[field])

        if not update_fields:
            return jsonify({
                "message": "No valid fields provided for update"
            }), 400

        query = f"""
            UPDATE customers
            SET {', '.join(update_fields)}
            WHERE customer_id = %s
        """

        values.append(customer_id)

        cursor.execute(query, tuple(values))
        connection.commit()

        return jsonify({
            "message": "Customer updated successfully!",
            "status": "Success"
        }), 200

    except Exception as e:
        connection.rollback()

        return jsonify({
            "message": "Failed to update customer",
            "error": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()

        connection.close()
@customers_bp.route("/api/customers/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id):

    connection = get_db_connection()

    if not connection:
        return jsonify({
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:
        cursor = connection.cursor()

        query = """
            DELETE FROM customers
            WHERE customer_id = %s
        """

        cursor.execute(query, (customer_id,))

        if cursor.rowcount == 0:
            return jsonify({
                "message": "Customer not found"
            }), 404

        connection.commit()

        return jsonify({
            "message": "Customer deleted successfully!",
            "status": "Success"
        }), 200

    except Exception as e:
        connection.rollback()

        return jsonify({
            "message": "Failed to delete customer",
            "error": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()

        connection.close()