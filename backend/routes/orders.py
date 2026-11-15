
from flask import Blueprint, request, jsonify
from database import get_db_connection
from ai.duplicate_detector import is_duplicate_order
from decimal import Decimal, InvalidOperation

orders_bp = Blueprint("orders", __name__)


# CREATE ORDER WITH MULTIPLE PRODUCTS
@orders_bp.route("/api/orders", methods=["POST"])
def create_order():

    data = request.get_json()

    if data is None:
        return jsonify({"message": "Invalid JSON data"}), 400

    required_fields = ["seller_id", "customer_id", "items"]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "message": f"{field} is required"
            }), 400

    items = data["items"]

    if not isinstance(items, list) or len(items) == 0:
        return jsonify({
            "message": "At least one product is required"
        }), 400

    try:
        seller_id = int(data["seller_id"])
        customer_id = int(data["customer_id"])

        if seller_id <= 0 or customer_id <= 0:
            raise ValueError()

        product_ids = []
        validated_items = []

        for item in items:

            if not isinstance(item, dict):
                raise ValueError()

            product_id = int(item["product_id"])
            quantity = int(item["quantity"])

            if product_id <= 0 or quantity <= 0:
                raise ValueError()

            if product_id in product_ids:
                return jsonify({
                    "message": "Duplicate product_id in items. Combine its quantity."
                }), 400

            product_ids.append(product_id)

            validated_items.append({
                "product_id": product_id,
                "quantity": quantity
            })

    except (ValueError, TypeError, KeyError):
        return jsonify({
            "message": "Invalid seller, customer, product or quantity"
        }), 400

    connection = get_db_connection()

    if not connection:
        return jsonify({
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        # Verify customer belongs to this seller
        cursor.execute("""
            SELECT customer_id, phone
            FROM customers
            WHERE customer_id = %s AND seller_id = %s
        """, (customer_id, seller_id))

        customer = cursor.fetchone()

        if not customer:
            return jsonify({
                "message": "Customer not found for this seller"
            }), 404

        # Get product information and prices from database
        placeholders = ", ".join(["%s"] * len(product_ids))

        query = f"""
            SELECT product_id, product_name, price
            FROM products
            WHERE seller_id = %s
            AND product_id IN ({placeholders})
        """

        cursor.execute(query, (seller_id, *product_ids))
        products = cursor.fetchall()

        if len(products) != len(product_ids):
            return jsonify({
                "message": "One or more products were not found for this seller"
            }), 404

        product_map = {
            product["product_id"]: product
            for product in products
        }

        # Calculate total using database prices
        total_amount = Decimal("0.00")

        for item in validated_items:
            product = product_map[item["product_id"]]
            unit_price = Decimal(str(product["price"]))

            item["unit_price"] = unit_price
            item["subtotal"] = unit_price * item["quantity"]

            total_amount += item["subtotal"]

        # Find possible duplicate orders from the last 24 hours
        duplicate_candidates = []

        if customer["phone"]:

            duplicate_query = """
                SELECT
                    o.order_id,
                    o.order_date,
                    c.phone,
                    p.product_name,
                    oi.quantity
                FROM orders o
                JOIN customers c
                    ON o.customer_id = c.customer_id
                JOIN order_items oi
                    ON o.order_id = oi.order_id
                JOIN products p
                    ON oi.product_id = p.product_id
                WHERE o.seller_id = %s
                AND c.phone = %s
                AND o.order_date >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
                AND o.order_status != 'Cancelled'
            """

            cursor.execute(
                duplicate_query,
                (seller_id, customer["phone"])
            )

            existing_items = cursor.fetchall()

            for new_item in validated_items:

                new_product = product_map[new_item["product_id"]]

                new_order = {
                    "phone": customer["phone"],
                    "product_name": new_product["product_name"],
                    "quantity": new_item["quantity"]
                }

                for old_item in existing_items:

                    existing_order = {
                        "phone": old_item["phone"],
                        "product_name": old_item["product_name"],
                        "quantity": old_item["quantity"]
                    }

                    if is_duplicate_order(new_order, existing_order):

                        duplicate_candidates.append({
                            "existing_order_id": old_item["order_id"],
                            "product_name": old_item["product_name"],
                            "quantity": old_item["quantity"],
                            "order_date": old_item["order_date"].isoformat()
                        })

        # Do not save until seller confirms possible duplicate
        if duplicate_candidates and data.get("confirm_duplicate") is not True:

            return jsonify({
                "message": "Possible duplicate order detected!",
                "duplicate_warning": True,
                "requires_confirmation": True,
                "duplicate_candidates": duplicate_candidates,
                "instruction": "Send the same request again with confirm_duplicate=true if this is a genuine new order.",
                "status": "Warning"
            }), 409

        # Save order and items together
        cursor.execute("""
            INSERT INTO orders
            (
                seller_id,
                customer_id,
                total_amount,
                payment_method,
                order_status,
                delivery_status
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            seller_id,
            customer_id,
            total_amount,
            data.get("payment_method", "COD"),
            data.get("order_status", "Pending"),
            data.get("delivery_status", "Pending")
        ))

        order_id = cursor.lastrowid

        for item in validated_items:

            cursor.execute("""
                INSERT INTO order_items
                (
                    order_id,
                    product_id,
                    quantity,
                    unit_price,
                    subtotal
                )
                VALUES (%s, %s, %s, %s, %s)
            """, (
                order_id,
                item["product_id"],
                item["quantity"],
                item["unit_price"],
                item["subtotal"]
            ))

        connection.commit()

        return jsonify({
            "message": "Order created successfully!",
            "order_id": order_id,
            "total_amount": str(total_amount),
            "total_products": len(validated_items),
            "duplicate_warning": bool(duplicate_candidates),
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


# GET ALL ORDERS
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

        cursor.execute("""
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
        """)

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


# GET SINGLE ORDER
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

        cursor.execute("""
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
        """, (order_id,))

        order = cursor.fetchone()

        if not order:
            return jsonify({
                "message": "Order not found"
            }), 404

        cursor.execute("""
            SELECT
                oi.item_id,
                oi.product_id,
                p.product_name,
                oi.quantity,
                oi.unit_price,
                oi.subtotal
            FROM order_items oi
            JOIN products p
                ON oi.product_id = p.product_id
            WHERE oi.order_id = %s
        """, (order_id,))

        order["items"] = cursor.fetchall()

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


# UPDATE ORDER
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


# DELETE ORDER
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

        cursor.execute("""
            DELETE FROM order_items
            WHERE order_id = %s
        """, (order_id,))

        cursor.execute("""
            DELETE FROM orders
            WHERE order_id = %s
        """, (order_id,))

        if cursor.rowcount == 0:
            connection.rollback()
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
