
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

    match = re.search(
        r'(?<!\d)01\d{2,13}(?!\d)',
        message
    )

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

    # English numeric quantity: I need 2 shirts
    match = re.search(
        r'\b(?:need|want|order)\s+(\d+)\b',
        message,
        re.IGNORECASE
    )

    if match:
        return int(match.group(1))

    # Bangla and Banglish numeric quantity
    match = re.search(
        r'(\d+)\s*(?:টা|টি|ta|pcs?|pieces?)',
        message,
        re.IGNORECASE
    )

    if match:
        return int(match.group(1))

    # Quantity words
    if re.search(
        r'একটা|একটি|\bone\b|\ba\b|\ban\b',
        message,
        re.IGNORECASE
    ):
        return 1

    return 1


# Extract product name
def extract_product(message):
    message = normalize_digits(message)

    patterns = [
        # English numeric quantity: I need 2 Black Shirt
        r'\b(?:need|want|order)\s+\d+\s+(.+?)(?=\s*(?:price|phone|address)|$)',

        # Bangla quantity
        r'(?:\d+\s*(?:টা|টি))\s+(.+?)(?=\s*(?:দাম|ফোন|ঠিকানা|নিবো|নেবো|দেন|চাই)|$)',

        # Banglish quantity
        r'(?:\d+\s*(?:ta|pcs?|pieces?))\s+(.+?)(?=\s*(?:price|phone|address|nibo|nebo|chai|den)|$)',

        # Bangla quantity words
        r'(?:একটা|একটি)\s+(.+?)(?=\s*(?:দাম|ফোন|ঠিকানা|নিবো|নেবো|দেন|চাই)|$)',

        # English without numeric quantity
        r'(?:need|want)\s+(?:(?:a|an|one)\s+)?(.+?)(?=\s*(?:price|phone|address)|$)',

        # Bangla with greeting
        r'(?:আপু|আপা|ভাইয়া|ভাই)\s+(.+?)\s*(?:নিবো|নেবো|নিতে চাই|চাই|দেন|নিব|নেব)',

        # Bangla without greeting
        r'(.+?)\s*(?:নিবো|নেবো|নিতে চাই|চাই|নিব|নেব)',

        # Banglish without quantity
        r'(?:apu|apa|vaiya|vai)\s+(.+?)\s*(?:nibo|nebo|chai|den)',

        # English product name
        r'(?:buy|order)\s+(.+?)(?=\s*(?:price|phone|address)|$)'
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            message,
            re.IGNORECASE
        )

        if match:
            product = match.group(1).strip()

            # Remove phone number
            product = re.sub(
                r'(?<!\d)01\d{2,13}(?!\d)',
                '',
                product
            ).strip()

            # Remove price information
            product = re.sub(
                r'\b(?:price|দাম)\s*[:=]?\s*\d+(?:\.\d+)?',
                '',
                product,
                flags=re.IGNORECASE
            ).strip()

            # Remove greeting
            product = re.sub(
                r'^(?:আপু|আপা|ভাইয়া|ভাই|apu|apa|vaiya|vai)\s+',
                '',
                product,
                flags=re.IGNORECASE
            ).strip()

            # Remove trailing punctuation
            product = re.sub(
                r'[.,!?;:]+$',
                '',
                product
            ).strip()

            if product:
                return product

    return None


# Extract delivery address
def extract_address(message):
    message = normalize_digits(message)

    patterns = [
        r'ঠিকানা\s+(.+)',
        r'address\s+(.+)',
        r'বাসা\s+(.+)'
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            message,
            re.IGNORECASE
        )

        if match:
            address = match.group(1).strip()

            # Remove phone number from address
            address = re.sub(
                r'(?<!\d)01\d{2,13}(?!\d)',
                '',
                address
            ).strip()

            return address

    return None


# Extract all order information
def extract_order(message):
    return {
        "product_name": extract_product(message),
        "quantity": extract_quantity(message),
        "unit_price": extract_price(message),
        "phone": extract_phone(message),
        "address": extract_address(message)
    }
