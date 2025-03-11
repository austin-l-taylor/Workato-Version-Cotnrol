import jwt
import time
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()  

class GithubAuth:
    def __init__(self, client_id, private_key):  
        self.client_id = client_id
        self.pem_path = private_key
        
    def get_jwt(self):    
        pem_path = self.pem_path
        # Create JWT payload
        payload = {
            'iat': int(time.time()), # Issued at time
            'exp': int(time.time()) + 600, # JWT expiration time (10 minutes maximum)
            'iss': self.client_id # GitHub App's client ID
        }
        
        encoded_jwt = jwt.encode(payload, pem_path, algorithm='RS256') # Create JWT

        return encoded_jwt  

    def authenticate_app(self, jwt):
        # Get the installation access token
        url = f"https://api.github.com/app/installations"
        headers = {
            "Authorization": f"Bearer {jwt}",
            "Accept": "application/vnd.github.v3+json", 
            "X-Github-Api-Version": "2022-11-28"
        }
        response = requests.get(url, headers=headers)

        installations = response.json()
        installation_id = installations[0]['id']
        
        token_url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
        token_response = requests.post(token_url, headers=headers)
        access_token = token_response.json()['token']
        
        headers["Authorization"] = f"Bearer {access_token}"
        
        return headers

