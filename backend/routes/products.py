
from flask import Blueprint, request, jsonify
from database import get_db_connection

products_bp = Blueprint("products", __name__)


# Create a new product
@products_bp.route("/api/products", methods=["POST"])
def create_product():

    data = request.get_json()

    if data is None:
        return jsonify({
            "message": "Invalid JSON data"
        }), 400

    required_fields = ["seller_id", "product_name", "price"]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "message": f"{field} is required"
            }), 400

    try:
        price = float(data["price"])
        stock_quantity = int(data.get("stock_quantity", 0))

        if price < 0 or stock_quantity < 0:
            return jsonify({
                "message": "Price and stock cannot be negative"
            }), 400

    except (ValueError, TypeError):
        return jsonify({
            "message": "Invalid price or stock quantity"
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
            INSERT INTO products
            (seller_id, product_name, description, price, stock_quantity)
            VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            data["seller_id"],
            data["product_name"],
            data.get("description"),
            price,
            stock_quantity
        )

        cursor.execute(query, values)
        connection.commit()

        return jsonify({
            "message": "Product created successfully!",
            "product_id": cursor.lastrowid,
            "status": "Success"
        }), 201

    except Exception as e:
        connection.rollback()

        return jsonify({
            "message": "Failed to create product",
            "error": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()

        connection.close()


# Get all products
@products_bp.route("/api/products", methods=["GET"])
def get_all_products():

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
                product_id,
                seller_id,
                product_name,
                description,
                price,
                stock_quantity,
                created_at
            FROM products
            ORDER BY product_id DESC
        """

        cursor.execute(query)
        products = cursor.fetchall()

        return jsonify({
            "message": "Products retrieved successfully!",
            "total_products": len(products),
            "products": products,
            "status": "Success"
        }), 200

    except Exception as e:
        return jsonify({
            "message": "Failed to retrieve products",
            "error": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()

        connection.close()
