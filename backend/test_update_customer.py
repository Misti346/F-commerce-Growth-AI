import requests

customer_id = 1

url = f"http://127.0.0.1:5000/api/customers/{customer_id}"

data = {
    "customer_name": "Updated Test Customer",
    "phone": "01900000000",
    "address": "Chandpur, Bangladesh"
}

response = requests.put(url, json=data)

print("Status Code:", response.status_code)
print("Response:", response.json())