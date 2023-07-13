import http.client
import json


def get_access_token():
    conn = http.client.HTTPSConnection("dev-ca7x87dj.us.auth0.com")
    payload = '{"client_id":"FMG1uFUNlBEeCc0xu8mhHDeHx5P56fsi","client_secret":"V4xf2hnmoYqt-4HNu0psJ98b6W-GEzYf7lpu264ksN-XCGUCCYu807uUIqmQxZLT","audience":"https://bookstore/api","grant_type":"client_credentials"}'
    headers = {"content-type": "application/json"}
    conn.request("POST", "/oauth/token", payload, headers)
    res = conn.getresponse()
    data = res.read()
    token_data = json.loads(data.decode("utf-8"))
    return token_data["access_token"]
