import requests

# request = requests.get('http://127.0.0.1:8000/items')

# print(request.json())

print(requests.get("http://127.0.0.1:8000/items?name=Drill").json())