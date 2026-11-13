import requests

url = "http://127.0.0.1:5000/api/orders/1"

updated_data = {
    "order_status": "Confirmed",
    "delivery_status": "Processing"
}

response = requests.put(url, json=updated_data)

print("Status Code:", response.status_code)
print("Response:", response.json())