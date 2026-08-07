import requests
import logging

from .client import client_config
from .secrets import client_key, login_key


def logout():
    token = login_key.get()
    
    client_id = client_config.get()
    client_secret = client_key.get()

    try:
        response = requests.delete(
            f"https://api.github.com/applications/{client_id}/token",
            auth=(client_id, client_secret),
            headers={
                "Accept": "application/vnd.github+json",
            },
            json={
                "access_token": token,
            },
        )

        response.raise_for_status()
        logging.info("GitHub token revoked.")

    finally:
        login_key.delete()
        logging.info("Local token removed.")