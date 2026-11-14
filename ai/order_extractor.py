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

    match = re.search(r'(?<!\d)01\d{2,13}(?!\d)', message)

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

    if match:
        return int(match.group(1))

    if re.search(r'একটা|একটি|\bone\b', message, re.IGNORECASE):
        return 1

    return 1


# Extract product name
def extract_product(message):
    message = normalize_digits(message)

    patterns = [
        # Bangla quantity: 2 ta কালো জামা
        r'(?:\d+\s*(?:টা|টি))\s+(.+?)(?=\s*(?:দাম|ফোন|ঠিকানা|নিবো|নেবো|দেন|চাই)|$)',

        # Banglish quantity: 2 ta shirt
        r'(?:\d+\s*(?:ta|pcs?|pieces?))\s+(.+?)(?=\s*(?:price|phone|address|nibo|nebo|chai|den)|$)',

        # Bangla quantity words
        r'(?:একটা|একটি)\s+(.+?)(?=\s*(?:দাম|ফোন|ঠিকানা|নিবো|নেবো|দেন|চাই)|$)',

        # English: I need a bag / want a shirt
        r'(?:need|want)\s+(?:(?:a|an|one)\s+)?(.+?)(?=\s*(?:price|phone|address)|$)',

        # Bangla without quantity: আপু কালো জামা নিবো
        r'(?:আপু|আপা|ভাইয়া|ভাই)\s+(.+?)\s*(?:নিবো|নেবো|নিতে চাই|চাই|দেন|নিব|নেব)',

        # Bangla without greeting: কালো জামা নিবো
        r'(.+?)\s*(?:নিবো|নেবো|নিতে চাই|চাই|নিব|নেব)',

        # Banglish without quantity: কালো জামা nibo
        r'(?:apu|apa|vaiya|vai)\s+(.+?)\s*(?:nibo|nebo|chai|den)',

        # English product name without quantity
        r'(?:buy|order)\s+(.+?)(?=\s*(?:price|phone|address)|$)'
    ]

    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)

        if match:
            product = match.group(1).strip()

            # Remove common greeting words if captured
            product = re.sub(
                r'^(?:আপু|আপা|ভাইয়া|ভাই|apu|apa|vaiya|vai)\s+',
                '',
                product,
                flags=re.IGNORECASE
            )

            if product:
                return product

    return None


# Extract delivery address
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


# Extract all order information
def extract_order(message):
    return {
        "product_name": extract_product(message),
        "quantity": extract_quantity(message),
        "unit_price": extract_price(message),
        "phone": extract_phone(message),
        "address": extract_address(message)
    }