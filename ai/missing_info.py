import re
from ai.order_extractor import extract_order
def validate_phone(phone):
    if not phone:
        return False

    return bool(re.fullmatch(r'01[3-9]\d{8}', phone))


def detect_missing_info(message):
    order = extract_order(message)

    missing_fields = []
    invalid_fields = []

    required_fields = {
        "product_name": "Product Name",
        "phone": "Phone Number",
        "address": "Delivery Address"
    }

    for field, label in required_fields.items():
        if not order[field]:
            missing_fields.append(label)

    if order["phone"] and not validate_phone(order["phone"]):
        invalid_fields.append("Phone Number")

    return {
        "order_details": order,
        "missing_fields": missing_fields,
        "invalid_fields": invalid_fields,
        "is_complete": len(missing_fields) == 0 and len(invalid_fields) == 0
    }