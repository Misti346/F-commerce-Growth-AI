
from flask import Blueprint, request, jsonify

from ai.missing_info import detect_missing_info
from ai.duplicate_detector import is_duplicate_order
from database import get_db_connection


ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/api/ai/extract-order", methods=["POST"])
def extract_order_api():

    data = request.get_json(silent=True)

    if not data or "message" not in data:
        return jsonify({
            "status": "Error",
            "message": "Customer message is required"
        }), 400

    message = data["message"]

    if not isinstance(message, str) or not message.strip():
        return jsonify({
            "status": "Error",
            "message": "Message must be a non-empty string"
        }), 400

    try:
        seller_id = int(data.get("seller_id", 0))

        if seller_id <= 0:
            return jsonify({
                "status": "Error",
                "message": "Valid seller_id is required"
            }), 400

    except (ValueError, TypeError):
        return jsonify({
            "status": "Error",
            "message": "Invalid seller_id"
        }), 400

    connection = None
    cursor = None

    try:
        result = detect_missing_info(message)

        order = result["order_details"]

        duplicate_candidates = []
        duplicate_check_performed = False

        phone = order.get("phone")
        product_name = order.get("product_name")
        quantity = order.get("quantity")

        phone_is_valid = (
            phone
            and "Phone Number" not in result["invalid_fields"]
        )

        if phone_is_valid and product_name and quantity:

            connection = get_db_connection()

            if not connection:
                return jsonify({
                    "status": "Error",
                    "message": "Database connection failed"
                }), 500

            cursor = connection.cursor(dictionary=True)

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
                (seller_id, phone)
            )

            existing_items = cursor.fetchall()

            new_order = {
                "phone": phone,
                "product_name": product_name,
                "quantity": quantity
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

            duplicate_check_performed = True

        return jsonify({
            "status": "Success",
            "message": "Order information extracted successfully",
            "order_draft": order,
            "missing_fields": result["missing_fields"],
            "invalid_fields": result["invalid_fields"],
            "confidence": result["confidence"],
            "is_complete": result["is_complete"],
            "duplicate_check_performed": duplicate_check_performed,
            "duplicate_warning": bool(duplicate_candidates),
            "duplicate_candidates": duplicate_candidates,
            "requires_seller_review": True
        }), 200

    except Exception:
        return jsonify({
            "status": "Error",
            "message": "Unable to process customer message"
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()
