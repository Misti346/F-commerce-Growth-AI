import requests

url = "http://127.0.0.1:5000/api/customers"

data = {
    "seller_id": 1,
    "customer_name": "API Test Customer",
    "phone": "01800000000",
    "address": "Dhaka, Bangladesh"
}

response = requests.post(url, json=data)

print("Status Code:", response.status_code)
print("Response:", response.json())