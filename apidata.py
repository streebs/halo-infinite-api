import requests
import httpx

from auth_manager import _spartan_token, _343_clearance

def request_data(method : str, url : str, data = {}):
    token = _spartan_token()
    headers = {
        "User-Agent": "OpenSpartan.Career/1.0",
        "Accept-Language": "us-en",
        "X-343-Authorization-Spartan": token,
        "Accept": "application/json",
        "343-clearance": _343_clearance(token).get("FlightConfigurationId", "Clearance Not Found")
        
    }
    response = httpx.request(method, url, headers=headers)

    
    # response = requests.request(method, url)
    if response.status_code == 200:
        return response.json()
    else:
        return response.json()
    