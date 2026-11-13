
import requests

url = "http://127.0.0.1:5000/api/orders"

order_data = {
    "seller_id": 1,
    "customer_id": 1,
    "total_amount": 3500,
    "payment_method": "COD"
}

response = requests.post(url, json=order_data)

print("Status Code:", response.status_code)
print("Response:", response.json())
