
from flask import Blueprint, request, jsonify
from database import get_db_connection

orders_bp = Blueprint("orders", __name__)

@orders_bp.route("/api/orders", methods=["POST"])
def create_order():
    data = request.get_json()

    if data is None:
        return jsonify({"message": "Invalid JSON data"}), 400

    required_fields = ["seller_id", "customer_id", "total_amount"]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "message": f"{field} is required"
            }), 400

    connection = get_db_connection()

    if not connection:
        return jsonify({"message": "Database connection failed"}), 500

    cursor = None

    try:
        cursor = connection.cursor()

        query = """
            INSERT INTO orders
            (seller_id, customer_id, total_amount,
             payment_method, order_status, delivery_status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            data["seller_id"],
            data["customer_id"],
            data["total_amount"],
            data.get("payment_method", "COD"),
            data.get("order_status", "Pending"),
            data.get("delivery_status", "Pending")
        )

        cursor.execute(query, values)
        connection.commit()
        return jsonify({
            "message": "Order created successfully!",
            "order_id": cursor.lastrowid,
            "status": "Success"
        }), 201

    except Exception as e:
        connection.rollback()
        return jsonify({
            "message": "Failed to create order",
            "error": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
        connection.close()

@orders_bp.route("/api/orders", methods=["GET"])
def get_all_orders():

    connection = get_db_connection()

    if not connection:
        return jsonify({
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                o.order_id,
                o.seller_id,
                o.customer_id,
                c.customer_name,
                c.phone,
                c.address,
                o.order_date,
                o.total_amount,
                o.payment_method,
                o.order_status,
                o.delivery_status
            FROM orders o
            JOIN customers c
            ON o.customer_id = c.customer_id
            ORDER BY o.order_id DESC
        """

        cursor.execute(query)
        orders = cursor.fetchall()

        return jsonify({
            "orders": orders,
            "count": len(orders),
            "status": "Success"
        }), 200

    except Exception as e:
        return jsonify({
            "message": "Failed to fetch orders",
            "error": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()

        connection.close() 

@orders_bp.route("/api/orders/<int:order_id>", methods=["GET"])
def get_single_order(order_id):

    connection = get_db_connection()

    if not connection:
        return jsonify({
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                o.order_id,
                o.seller_id,
                o.customer_id,
                c.customer_name,
                c.phone,
                c.address,
                o.order_date,
                o.total_amount,
                o.payment_method,
                o.order_status,
                o.delivery_status
            FROM orders o
            JOIN customers c
            ON o.customer_id = c.customer_id
            WHERE o.order_id = %s
        """

        cursor.execute(query, (order_id,))
        order = cursor.fetchone()

        if not order:
            return jsonify({
                "message": "Order not found"
            }), 404

        return jsonify({
            "order": order,
            "status": "Success"
        }), 200

    except Exception as e:
        return jsonify({
            "message": "Failed to fetch order",
            "error": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()

        connection.close()
@orders_bp.route("/api/orders/<int:order_id>", methods=["PUT"])
def update_order(order_id):

    data = request.get_json()

    if data is None:
        return jsonify({
            "message": "Invalid JSON data"
        }), 400

    allowed_fields = [
        "total_amount",
        "payment_method",
        "order_status",
        "delivery_status"
    ]

    update_fields = {
        key: data[key]
        for key in allowed_fields
        if key in data
    }

    if not update_fields:
        return jsonify({
            "message": "No valid fields provided for update"
        }), 400

    connection = get_db_connection()

    if not connection:
        return jsonify({
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:
        cursor = connection.cursor()

        set_clause = ", ".join(
            f"{field} = %s" for field in update_fields
        )

        query = f"""
            UPDATE orders
            SET {set_clause}
            WHERE order_id = %s
        """

        values = tuple(update_fields.values()) + (order_id,)

        cursor.execute(query, values)

        if cursor.rowcount == 0:
            cursor.execute(
                "SELECT order_id FROM orders WHERE order_id = %s",
                (order_id,)
            )

            if not cursor.fetchone():
                return jsonify({
                    "message": "Order not found"
                }), 404

        connection.commit()

        return jsonify({
            "message": "Order updated successfully!",
            "order_id": order_id,
            "updated_fields": list(update_fields.keys()),
            "status": "Success"
        }), 200

    except Exception as e:
        connection.rollback()

        return jsonify({
            "message": "Failed to update order",
            "error": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()

        connection.close()

@orders_bp.route("/api/orders/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):

    connection = get_db_connection()

    if not connection:
        return jsonify({
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:
        cursor = connection.cursor()

        query = """
            DELETE FROM orders
            WHERE order_id = %s
        """

        cursor.execute(query, (order_id,))

        if cursor.rowcount == 0:
            return jsonify({
                "message": "Order not found"
            }), 404

        connection.commit()

        return jsonify({
            "message": "Order deleted successfully!",
            "order_id": order_id,
            "status": "Success"
        }), 200

    except Exception as e:
        connection.rollback()

        return jsonify({
            "message": "Failed to delete order",
            "error": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()

        connection.close()