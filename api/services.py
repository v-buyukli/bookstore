import http.client
import json

from django.conf import settings


def get_access_token():
    conn = http.client.HTTPSConnection(settings.AUTH0_DOMAIN)
    payload_dict = {
        "client_id": {settings.AUTH0_CLIENT_ID},
        "client_secret": {settings.AUTH0_CLIENT_SECRET},
        "audience": "https://bookstore/api",
        "grant_type": "client_credentials",
    }
    payload = str(payload_dict)
    headers = {"content-type": "application/json"}
    conn.request("POST", "/oauth/token", payload, headers)
    res = conn.getresponse()
    data = res.read()
    token_data = json.loads(data.decode("utf-8"))
    return token_data["access_token"]
