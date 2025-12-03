import requests
import base64
from requests.auth import HTTPBasicAuth

def test_auth():
    url = "https://api.d-id.com/talks"
    
    # Credentials
    email = "nsubugacollin@gmail.com"
    password = "M21ye8rOIk5vlxy2Dko70"
    
    print(f"Testing auth for: {email}")
    
    # Method 1: HTTPBasicAuth (Let requests handle encoding)
    print("\n--- Method 1: HTTPBasicAuth ---")
    try:
        response = requests.get(url, auth=HTTPBasicAuth(email, password))
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

    # Method 2: Manual Base64
    print("\n--- Method 2: Manual Base64 ---")
    try:
        raw_creds = f"{email}:{password}"
        encoded_key = base64.b64encode(raw_creds.encode('utf-8')).decode('utf-8')
        headers = {
            "Authorization": f"Basic {encoded_key}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

    # Method 3: Maybe the user provided string IS the key (unlikely but checking)
    print("\n--- Method 3: Raw Provided String ---")
    try:
        provided = "bnN1YnVnYWNvbGxpbkBnbWFpbC5jb20:M21ye8rOIk5vlxy2Dko70"
        headers = {
            "Authorization": f"Basic {provided}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_auth()
