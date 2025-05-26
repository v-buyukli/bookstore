import http.client
import json

from django.conf import settings


def get_access_token():
    conn = http.client.HTTPSConnection(settings.AUTH0_DOMAIN)
    payload = json.dumps(
        {
            "client_id": settings.AUTH0_CLIENT_ID,
            "client_secret": settings.AUTH0_CLIENT_SECRET,
            "audience": "https://bookstore/api",
            "grant_type": "client_credentials",
        }
    )
    headers = {"content-type": "application/json"}
    conn.request("POST", "/oauth/token", payload, headers)
    res = conn.getresponse()
    data = res.read()

    if res.status != 200:
        raise Exception(f"Auth0 error: {res.status} - {data.decode()}")

    token_data = json.loads(data)
    return token_data["access_token"]
