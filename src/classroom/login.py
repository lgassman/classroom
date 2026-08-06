
import webbrowser
from .pkce import generate_pkce
from urllib.parse import urlencode, parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from .secrets import client_key, login_key
from .config import client_config

import logging 
import threading

AUTH_URL = "https://github.com/login/oauth/authorize"
TOKEN_URL = "https://github.com/login/oauth/access_token"

def open_browser(url):
    def run():
        if not webbrowser.open(url):
            raise Exception("Could not open browser")

    threading.Thread(target=run, daemon=True).start()

def login():
    verifier, challenge = generate_pkce()
    client_secret = client_key.get()

    
    server, redirect_url = start_callback_server()
    print(redirect_url)


    params = {
        "client_id": client_config.get(),
        "redirect_uri": redirect_url,
        "response_type": "code",
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "scope": "repo"
    }

    url = f"{AUTH_URL}?{urlencode(params)}"

    print("Opening browser...")
    open_browser(url)
    print("Browser abierto")

    server.handle_request()

    if server.error:
        raise RuntimeError(server.error)
    if not server.code:
        raise RuntimeError("No authorization code received")

    server.server_close()

    response = requests.post(
        TOKEN_URL,
        json={
            "client_id": client_config.get(),
            "code": server.code,
            "redirect_uri": redirect_url,
            "code_verifier": verifier,
            "client_secret": client_secret,

        },
        headers={
            "Accept": "application/json",
        },
    )

    response.raise_for_status()
    
    data = response.json()

    if "access_token" not in data:
        raise RuntimeError(
            f"GitHub token exchange failed: {data}"
        )

    login_key.save(data["access_token"])

class CallbackHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        print("NEW CONNECTION")
        super().__init__(*args, **kwargs)

    def do_GET(self):
        print("Callback received:", self.path)
        query = parse_qs(urlparse(self.path).query)
        self.server.code = query.get("code", [None])[0]
        self.server.error = query.get("error", [None])[0]

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        self.wfile.write(
            b"<h1>Login completed. You can close this window.</h1>"
        )


    def log_message(self, format, *args):
        logging.debug(format, *args)


def start_callback_server() -> tuple[HTTPServer, str]:
    
    server = HTTPServer(
        ("127.0.0.1", 0),
        CallbackHandler,
    )
    port = server.server_port
    server.daemon_threads = True
    redirect_uri = f"http://127.0.0.1:{port}/callback"
    
    return server, redirect_uri