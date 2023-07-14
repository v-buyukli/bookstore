import http.client
import json

from django.conf import settings


def get_access_token():
    conn = http.client.HTTPSConnection(settings.AUTH0_DOMAIN)
    payload = '{"client_id":"FMG1uFUNlBEeCc0xu8mhHDeHx5P56fsi","client_secret":"V4xf2hnmoYqt-4HNu0psJ98b6W-GEzYf7lpu264ksN-XCGUCCYu807uUIqmQxZLT","audience":"https://bookstore/api","grant_type":"client_credentials"}'
    headers = {"content-type": "application/json"}
    conn.request("POST", "/oauth/token", payload, headers)
    res = conn.getresponse()
    data = res.read()
    token_data = json.loads(data)
    return token_data["access_token"]
