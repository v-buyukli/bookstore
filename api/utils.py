import json

import jwt
import requests
from django.conf import settings


def jwt_get_username_from_payload_handler(payload):
    return "djangoauth0user"


def jwt_decode_token(token):
    header = jwt.get_unverified_header(token)
    jwks = requests.get(
        "https://{}/.well-known/jwks.json".format(settings.AUTH0_DOMAIN)
    ).json()
    public_key = None

    for jwk in jwks["keys"]:
        if jwk["kid"] == header["kid"]:
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

    if public_key is None:
        raise Exception("Public key not found.")

    issuer = "https://{}/".format(settings.AUTH0_DOMAIN)
    return jwt.decode(
        token,
        public_key,
        audience="https://bookstore/api",
        issuer=issuer,
        algorithms=["RS256"],
    )
