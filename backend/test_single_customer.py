import requests

customer_id = 1

url = f"http://127.0.0.1:5000/api/customers/{customer_id}"

response = requests.get(url)

print("Status Code:", response.status_code)
print("Response:", response.json())