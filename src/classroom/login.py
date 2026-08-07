
import webbrowser
from .pkce import generate_pkce
from urllib.parse import urlencode, parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from .secrets import client_key, login_key
from .client import client_config
from .whoami import whoami_response, print_whoami

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
    
    server = start_callback_server(verifier)


    params = {
        "client_id": client_config.get(),
        "redirect_uri": server.redirect_uri,
        "response_type": "code",
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "scope": "repo admin:org"
    }

    url = f"{AUTH_URL}?{urlencode(params)}"

    logging.debug("Opening browser...")
    open_browser(url)
    logging.debug("Browser abierto")

    server.handle_request()

    server.server_close()

    if not server.error:
        logging.info("Success!")
    else:
        logging.error("Failure!")

    if server.whoami:
        print_whoami(server.whoami)
        logging.info("If this is not the account you intended to use, log out from GitHub in your browser and try again.") 
    
class CallbackHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        client_secret = client_key.get()

        code = query.get("code", [None])[0]
        error = query.get("error", [None])[0]

        if error:
           self.write_response(error, 403)
           return

        if not code:
           self.write_response("No code received from github", 500)
           return


        response = requests.post(
            TOKEN_URL,
            json={
                "client_id": client_config.get(),
                "code": code,
                "redirect_uri": self.server.redirect_uri,
                "code_verifier":self.server.verifier,
                "client_secret": client_secret,

            },
            headers={
                "Accept": "application/json",
            },
        )

        try:
            data = response.json()
        except requests.JSONDecodeError:
            data = {}

        if response.status_code != 200:
            self.write_response( f"""
                <h1>GitHub authentication failed</h1>
                <p>{data.get("error_description", data.get("error", "Unknown error"))}</p>
            """, code=response.status_code)
            return


        if "access_token" not in data:
            self.write_response("No token in github responde", 500)
            return

        login_key.save(data["access_token"])
        self.server.success = True
        whoami_response_data = whoami_response()
        if whoami_response_data.status_code != 200:
            html = "Login is ok, but no data about the user"
        else:
            self.server.whoami = whoami_response_data
            user = whoami_response_data.json()
            html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>Classroom Login</title>
                </head>
                <body>
                    <h1>Login completed</h1>

                    <p>You are logged in as:</p>

                    <ul>
                        <li><strong>Login:</strong> {user["login"]}</li>
                        <li><strong>Name:</strong> {user.get("name") or "-"}</li>
                        <li><strong>Profile:</strong>
                            <a href="{user["html_url"]}">
                                {user["html_url"]}
                            </a>
                        </li>
                    </ul>

                    <p>
                        If this is not the account you intended to use:
                    </p>

                    <p>
                        <a href="https://github.com/logout">
                            Logout from GitHub
                        </a>
                        and run <code>classroom login</code> again.
                    </p>

                    <p>You can now close this window.</p>
                </body>
                </html>
                """

        self.write_response(html)


    def write_response(self, response, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        self.wfile.write(response.encode())
        if code != 200:
            self.server.error = response


    def log_message(self, format, *args):
        logging.debug(format, *args)


def start_callback_server(verifier: str) -> tuple[HTTPServer, str]:
    
    server = HTTPServer(
        ("127.0.0.1", 0),
        CallbackHandler,
    )
    port = server.server_port
    server.daemon_threads = True
    server.verifier = verifier
    server.redirect_uri = f"http://127.0.0.1:{port}/callback"
    server.error = None
    server.whoami = None
    return server