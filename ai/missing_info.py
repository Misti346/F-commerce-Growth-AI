
import re
from ai.order_extractor import extract_order, normalize_digits


# Validate Bangladeshi phone number
def validate_phone(phone):
    if not phone:
        return False

    return bool(re.fullmatch(r'01[3-9]\d{8}', phone))


# Calculate confidence score for extracted information
def calculate_confidence(order, message):
    confidence = {}

    # Product name confidence
    confidence["product_name"] = (
        85 if order["product_name"] else 0
    )

    # Quantity confidence
    normalized_message = normalize_digits(message)

    explicit_quantity = re.search(
        r'\d+\s*(?:টা|টি|ta|pcs?|pieces?)|একটা|একটি|\bone\b',
        normalized_message,
        re.IGNORECASE
    )

    if explicit_quantity:
        confidence["quantity"] = 95
    else:
        confidence["quantity"] = 70

    # Price confidence
    confidence["unit_price"] = (
        90 if order["unit_price"] is not None else 0
    )

    # Phone confidence
    if validate_phone(order["phone"]):
        confidence["phone"] = 100
    elif order["phone"]:
        confidence["phone"] = 30
    else:
        confidence["phone"] = 0

    # Address confidence
    confidence["address"] = (
        80 if order["address"] else 0
    )

    return confidence


# Detect missing and invalid order information
def detect_missing_info(message):
    order = extract_order(message)

    missing_fields = []
    invalid_fields = []

    required_fields = {
        "product_name": "Product Name",
        "phone": "Phone Number",
        "address": "Delivery Address"
    }

    # Check missing information
    for field, label in required_fields.items():
        if not order[field]:
            missing_fields.append(label)

    # Check invalid phone number
    if order["phone"] and not validate_phone(order["phone"]):
        invalid_fields.append("Phone Number")

    return {
        "order_details": order,
        "missing_fields": missing_fields,
        "invalid_fields": invalid_fields,
        "confidence": calculate_confidence(order, message),
        "is_complete": (
            len(missing_fields) == 0
            and len(invalid_fields) == 0
        )
    }
