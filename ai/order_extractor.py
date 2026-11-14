
import re

# Convert Bengali digits into English digits
def normalize_digits(text):
    bengali_digits = "০১২৩৪৫৬৭৮৯"
    english_digits = "0123456789"

    for bn, en in zip(bengali_digits, english_digits):
        text = text.replace(bn, en)

    return text


# Extract Bangladeshi phone number
def extract_phone(message):
    message = normalize_digits(message)

    match = re.search(r'01[3-9]\d{8}', message)

    return match.group() if match else None


# Extract product price
def extract_price(message):
    message = normalize_digits(message)

    match = re.search(
        r'(?:দাম|price)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(?:টাকা|taka|tk)?',
        message,
        re.IGNORECASE
    )

    return float(match.group(1)) if match else None


# Extract product quantity
def extract_quantity(message):
    message = normalize_digits(message)

    match = re.search(
        r'(\d+)\s*(?:টা|টি|ta|pcs?|pieces?)',
        message,
        re.IGNORECASE
    )

    return int(match.group(1)) if match else 1

def extract_product(message):
    message = normalize_digits(message)

    patterns = [
        r'একটা\s+(.+?)(?=\s+(?:দাম|ফোন|ঠিকানা|নিবো|দেন)|$)',
        r'একটি\s+(.+?)(?=\s+(?:দাম|ফোন|ঠিকানা|নিবো|দেন)|$)',
        r'(\d+)\s*(?:টা|টি)\s+(.+?)(?=\s+(?:দাম|ফোন|ঠিকানা)|$)',
        r'(\d+)\s+(?:ta|pcs?)\s+(.+?)(?=\s+(?:price|phone|address)|$)',
        r'(?:need|want)\s+(?:one\s+)?(.+?)(?=\s+(?:price|phone|address)|$)'
    ]

    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)

        if match:
            if len(match.groups()) == 2:
                return match.group(2).strip()
            return match.group(1).strip()

    return None

def extract_address(message):
    patterns = [
        r'ঠিকানা\s+(.+)',
        r'address\s+(.+)',
        r'বাসা\s+(.+)'
    ]

    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)

        if match:
            return match.group(1).strip()

    return None

def extract_order(message):
    return {
        "product_name": extract_product(message),
        "quantity": extract_quantity(message),
        "unit_price": extract_price(message),
        "phone": extract_phone(message),
        "address": extract_address(message)
    }
