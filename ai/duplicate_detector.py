# Check whether two orders are potential duplicates

def is_duplicate_order(new_order, existing_order):

    new_phone = new_order.get("phone")
    old_phone = existing_order.get("phone")

    new_product = new_order.get("product_name")
    old_product = existing_order.get("product_name")

    # Required information must exist
    if not all([new_phone, old_phone, new_product, old_product]):
        return False

    # Normalize values
    new_phone = str(new_phone).strip()
    old_phone = str(old_phone).strip()

    new_product = str(new_product).strip().lower()
    old_product = str(old_product).strip().lower()

    same_phone = new_phone == old_phone
    same_product = new_product == old_product

    same_quantity = (
        new_order.get("quantity")
        == existing_order.get("quantity")
    )

    return same_phone and same_product and same_quantity
