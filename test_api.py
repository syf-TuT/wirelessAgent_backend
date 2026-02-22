import requests

files = {'file': open(r'f:\code\wirelessAgent_backend\test_data_small.csv', 'rb')}
response = requests.post('http://localhost:8000/process-csv', files=files)
print('Status:', response.status_code)
print('Response:', response.json())