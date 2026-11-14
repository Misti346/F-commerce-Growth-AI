import pandas as pd

# Load dataset with correct data types
df = pd.read_csv(
    "dataset/order_messages.csv",
    dtype={
        "phone": "string",
        "address": "string",
        "customer_message": "string",
        "product_name": "string",
        "language": "string",
        "missing_fields": "string"
    }
)

print("DATASET PREVIEW")
print(df.head().to_string(index=False))

print("\nDATASET INFORMATION")
print(df.info())

print("\nMISSING VALUES")
print(df.isnull().sum())

print("\nTOTAL RECORDS:", len(df))
print("\nMISSING FIELD LABEL VALIDATION")

fields = ["unit_price", "phone", "address"]

for _, row in df.iterrows():
    expected = [
        field for field in fields
        if pd.isna(row[field])
    ]

    actual = (
        row["missing_fields"].split(";")
        if pd.notna(row["missing_fields"])
        else []
    )

    if set(expected) == set(actual):
        status = "CORRECT"
    else:
        status = "ERROR"

    print(
        f"ID: {row['message_id']} | "
        f"Expected: {expected} | "
        f"Actual: {actual} | {status}"
    )