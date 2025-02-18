import requests
import httpx

from auth_manager import _spartan_token

def request_data(method : str, url : str, data = {}):
    headers = {
        "User-Agent": "OpenSpartan.Career/1.0",
        "Accept-Language": "us-en",
        "X-343-Authorization-Spartan": _spartan_token(),
        "Accept": "application/json",
        
    }

    response = httpx.get(url, headers=headers)

    # response = requests.request(method, url)

    if response.status_code == 200:
        return response.json()
    else:
        return None
    