import requests

from .secrets import login_key
import logging

def whoami_response():
    return requests.get(
        "https://api.github.com/user",
        headers=login_key.headers()
    )

def print_whoami(response):
    if response.status_code == 401:
        logging.warning("Stored token is no longer valid.")
        return

    response.raise_for_status()

    user = response.json()

    logging.info(f"Login : {user['login']}")
    logging.info(f"Name  : {user.get('name') or '-'}")
    logging.info(f"Email : {user.get('email') or '-'}")
    logging.info(f"URL   : {user['html_url']}")


def whoami():
    print_whoami(whoami_response())

    
