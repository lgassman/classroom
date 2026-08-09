from .requests import request

from .secrets import login_key
import logging

def whoami_response():
    return request("GET","https://api.github.com/user")

def print_whoami(response):

    user = response.json()

    logging.info(f"Login : {user['login']}")
    logging.info(f"Name  : {user.get('name') or '-'}")
    logging.info(f"Email : {user.get('email') or '-'}")
    logging.info(f"URL   : {user['html_url']}")


def whoami():
    print_whoami(whoami_response())

    
