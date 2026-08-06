import requests

from .secrets import login_key

def whoami_response(token):
    return requests.get(
        "https://api.github.com/user",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
    )

def print_whoami(response):
    if response.status_code == 401:
        print("Stored token is no longer valid.")
        return

    response.raise_for_status()

    user = response.json()

    print(f"Login : {user['login']}")
    print(f"Name  : {user.get('name') or '-'}")
    print(f"Email : {user.get('email') or '-'}")
    print(f"URL   : {user['html_url']}")


def whoami():
    token = login_key.get()
    print_whoami(whoami_response(token))

    
