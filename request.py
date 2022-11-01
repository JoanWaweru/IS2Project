import requests

url = 'http://localhost:5000/predict_api'
r = requests.post(url,json={'negative':0, 'neutral':1, 'positive':2})

print(r.json())