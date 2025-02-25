from msal import PublicClientApplication, SerializableTokenCache
import os
import dotenv
import requests
import atexit
import json
from datetime import datetime, timezone


dotenv.load_dotenv('secrets/.azure')


CLIENT_ID = os.getenv('client_id')
SCOPES = ["Xboxlive.signin", "Xboxlive.offline_access"]
XBL_VERSION = "3.0"
TOKEN_CACHE_PATH = "secrets/.cache.bin"
SPARTAN_TOKEN_PATH = "secrets/.spartan-token.json"

cache = SerializableTokenCache()

def save_cache():
    if cache.has_state_changed:
        with open(TOKEN_CACHE_PATH, 'w') as token_cache_file:
            token_cache_file.write(cache.serialize())

def request_user_token(access_token):
    ticket_data = {
        "RelyingParty": "http://auth.xboxlive.com",
        "TokenType": "JWT",
        "Properties": {
            "AuthMethod": "RPS",
            "SiteName": "user.auth.xboxlive.com",
            "RpsTicket": f"d={access_token}"
        }
    }

    headers = {
        "x-xbl-contract-version": "1",
        "Content-Type": "application/json"
    }

    response = requests.post(
        url="https://user.auth.xboxlive.com/user/authenticate",
        json=ticket_data,
        headers=headers
    )

    if response.status_code == 200:
        return response.json()
    else:
        return None
    
# Request XSTS token from Halo Waypoint.
def request_xsts_token_halo(user_token):
    ticket_data = {
        "RelyingParty": "https://prod.xsts.halowaypoint.com/",
        "TokenType": "JWT",
        "Properties": {
            "UserTokens": [user_token],
            "SandboxId": "RETAIL"
        }
    }

    headers = {
        "x-xbl-contract-version": "1",
        "Content-Type": "application/json"
    }

    url = "https://xsts.auth.xboxlive.com/xsts/authorize"
    response = requests.post(url, json=ticket_data, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return None

def request_xsts_token_xbox(user_token):
    ticket_data = {
        "RelyingParty": "http://xboxlive.com",
        "TokenType": "JWT",
        "Properties": {
            "UserTokens": [user_token],
            "SandboxId": "RETAIL"
        }
    }

    headers = {
        "x-xbl-contract-version": "1",
        "Content-Type": "application/json"
    }

    url = "https://xsts.auth.xboxlive.com/xsts/authorize"
    response = requests.post(url, json=ticket_data, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return None
    
def get_xuid(gamertag, xsts_token_xbox):
    headers = {
        "x-xbl-contract-version": "3",
        "Content-Type": "application/json",
        "Authorization": xsts_token_xbox,
        "Accept-Language": "en-us"
    }
     
    url = f"https://peoplehub.xboxlive.com/users/me/people/search/decoration/detail,preferredColor?q={gamertag}&maxItems=25"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return None


def request_spartan_token(xsts_token):
    headers = {
        "Accept": "application/json",
        "User-Agent": "Halo API/v0.01" 
    }

    body = {
        "Audience": "urn:343:s3:services",
        "MinVersion": "4",
        "Proof": [
            {
                "Token": xsts_token,
                "TokenType": "Xbox_XSTSv3"
            }
        ]
    }
    url = 'https://settings.svc.halowaypoint.com/spartan-token'
    response = requests.request('POST', url, headers=headers, json=body)

    if response.status_code >= 200 and response.status_code <= 299:
        return response.json()
    else:
        return None
    

### Main Driver Code for Authentication
def _spartan_token():
    # First check if a spartan token already exists and has not expired
    with open(SPARTAN_TOKEN_PATH, 'r') as spartan_token:
        token_data = spartan_token.read()

        if token_data:
            token_json = json.loads(token_data)

            token_expiry_str = token_json['ExpiresUtc']['ISO8601Date']

            token_expiry = datetime.strptime(token_expiry_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            current_time = datetime.now(timezone.utc)

            if current_time > token_expiry:
                print("Spartan token has expired. Fetching new token...")
            else:
                return token_json.get('SpartanToken', 'Spartan Token Not Found')
        else:
            print("Spartan token was not cached locally. Fetching new token...")
            
        

    # Load token cache if exists
    if os.path.exists(TOKEN_CACHE_PATH):
        print("Loading token cache from disk")
        with open(TOKEN_CACHE_PATH, "r") as token_cache_file:
            cache.deserialize(token_cache_file.read())
        print("Loaded token cache from disk")

    atexit.register(save_cache)


    app = PublicClientApplication(
        CLIENT_ID,
        authority="https://login.microsoftonline.com/consumers",
        token_cache=cache
    )

    accounts = app.get_accounts()
    result = None

    # Acquire token.
    if accounts:
        print("Account exists in the cache.")
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
    else:
        print("No accounts in the cache")
        result = app.acquire_token_interactive(SCOPES)

    if result and 'access_token' in result:
        ticket = request_user_token(result['access_token'])

        if ticket:
            user_token = ticket.get('Token')
            user_hash = ticket.get('DisplayClaims', {}).get('xui', [{}])[0].get('uhs')

            xsts_ticket = request_xsts_token_halo(user_token)

            if xsts_ticket:
                xsts_token = xsts_ticket.get('Token')
                xbl_token = f'XBL{XBL_VERSION} x={user_hash};{xsts_token}'

                spartan_ticket = request_spartan_token(xsts_token)

                with open(SPARTAN_TOKEN_PATH, 'w') as spartan: # if a spartan token is being fetched then a new token must be written locally for caching purposes
                    spartan.write(json.dumps(spartan_ticket))

                return spartan_ticket.get('SpartanToken', 'Spartan Token Not Found')
            
def _xuid(gamertag):
    # Load token cache if exists
    if os.path.exists(TOKEN_CACHE_PATH):
        print("Loading token cache from disk")
        with open(TOKEN_CACHE_PATH, "r") as token_cache_file:
            cache.deserialize(token_cache_file.read())
        print("Loaded token cache from disk")

    atexit.register(save_cache)


    app = PublicClientApplication(
        CLIENT_ID,
        authority="https://login.microsoftonline.com/consumers",
        token_cache=cache
    )

    accounts = app.get_accounts()
    result = None

    # Acquire token.
    if accounts:
        print("Account exists in the cache.")
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
    else:
        print("No accounts in the cache")
        result = app.acquire_token_interactive(SCOPES)

    if result and 'access_token' in result:
        ticket = request_user_token(result['access_token'])

        if ticket:
            user_token = ticket.get('Token')
            user_hash = ticket.get('DisplayClaims', {}).get('xui', [{}])[0].get('uhs')

            xsts_ticket = request_xsts_token_xbox(user_token)

            if xsts_ticket:
                xsts_token = xsts_ticket.get('Token')
                xbl_token = f'XBL{XBL_VERSION} x={user_hash};{xsts_token}'

                user = get_xuid(gamertag, xbl_token)

                return user
            

