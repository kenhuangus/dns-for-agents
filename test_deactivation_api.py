import requests
import json

def test_deactivation():
    url = 'http://localhost:8082/deactivate'
    headers = {'Content-Type': 'application/json'}

    # 1. Deactivate an existing agent
    deactivate_req = {"agentName": "TestAgent"}
    print('\n--- Deactivate Existing Agent ---')
    response = requests.post(url, data=json.dumps(deactivate_req), headers=headers)
    print('Status Code:', response.status_code)
    print('Response:', response.json())

    # 2. Deactivate a non-existent agent
    deactivate_req = {"agentName": "NonExistentAgent"}
    print('\n--- Deactivate Non-Existent Agent ---')
    response = requests.post(url, data=json.dumps(deactivate_req), headers=headers)
    print('Status Code:', response.status_code)
    print('Response:', response.json())

    # 3. Invalid JSON
    print('\n--- Invalid JSON ---')
    response = requests.post(url, data='{bad json}', headers=headers)
    print('Status Code:', response.status_code)
    try:
        print('Response:', response.json())
    except Exception as e:
        print('Response could not be parsed:', e)

if __name__ == "__main__":
    test_deactivation()
