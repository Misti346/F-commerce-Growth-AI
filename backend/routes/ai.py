
from flask import Blueprint, request, jsonify

from ai.missing_info import detect_missing_info


ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/api/ai/extract-order", methods=["POST"])
def extract_order_api():

    data = request.get_json()

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
        result = detect_missing_info(message)

        return jsonify({
            "status": "Success",
            "message": "Order information extracted successfully",
            "order_draft": result["order_details"],
            "missing_fields": result["missing_fields"],
            "invalid_fields": result["invalid_fields"],
            "confidence": result["confidence"],
            "is_complete": result["is_complete"],
            "requires_seller_review": True
        }), 200

    except Exception as error:
        return jsonify({
            "status": "Error",
            "message": "Unable to process customer message"
        }), 500
