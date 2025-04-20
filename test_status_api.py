import requests


def test_status():
    url = 'http://localhost:8083/status'

    # 1. Query status for an existing agent
    print('\n--- Status of Existing Agent ---')
    params = {'agentName': 'TestAgent'}
    response = requests.get(url, params=params)
    print('Status Code:', response.status_code)
    print('Response:', response.json())

    # 2. Query status for a non-existent agent
    print('\n--- Status of Non-Existent Agent ---')
    params = {'agentName': 'NonExistentAgent'}
    response = requests.get(url, params=params)
    print('Status Code:', response.status_code)
    print('Response:', response.json())

    # 3. Query with missing agentName param
    print('\n--- Missing agentName Parameter ---')
    response = requests.get(url)
    print('Status Code:', response.status_code)
    print('Response:', response.text)

if __name__ == "__main__":
    test_status()
