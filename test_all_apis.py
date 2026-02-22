import requests

print("Testing /upload-csv endpoint...")
files = {'file': open(r'f:\code\wirelessAgent_backend\test_data_small.csv', 'rb')}
response = requests.post('http://localhost:8000/upload-csv', files=files)
print('Status:', response.status_code)
print('Response:', response.json())
print()

print("Testing /results endpoint...")
response = requests.get('http://localhost:8000/results')
print('Status:', response.status_code)
print('Response:', response.json())