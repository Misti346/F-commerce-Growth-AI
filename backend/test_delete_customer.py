import requests

customer_id = 2

url = f"http://127.0.0.1:5000/api/customers/{customer_id}"

response = requests.delete(url)

print("Status Code:", response.status_code)
print("Response:", response.json())