import json
import logging
import os
import random
import string
import threading
import webbrowser
from threading import Event

import requests
from flask import Flask, request

from saxo import SaxoConnection


class SaxoLogin:
    """Performs interactive login procedure, caches token in local file ~/.config/fin_bridge.json"""

    TOKEN_CACHE_FILE = os.path.expanduser("~/.config/fin_bridge.json")

    def __init__(self, app_config_filename: str):
        # read app config as json
        with open(app_config_filename, 'r') as f:
            app_config = json.load(f)
        # extract app key, secret, authentication url, and redirect url
        self.app_key = app_config['AppKey']
        self.app_secret = app_config['AppSecret']
        auth_url = app_config['AuthorizationEndpoint']
        self.redirect_url = app_config['RedirectUrls'][0]
        self.token_url = app_config['TokenEndpoint']
        # generate random state
        self.state = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
        # guess environment type from auth url
        if auth_url.startswith("https://sim."):
            self.environment = "simulation"
        else:
            self.environment = "live"
        # generate and open full authentication url
        self.auth_url = f"{auth_url}?response_type=code&client_id={self.app_key}&state={self.state}&redirect_uri={self.redirect_url}"

    def login(self) -> SaxoConnection:
        # try to read token from cache
        try:
            with open(self.TOKEN_CACHE_FILE, 'r') as f:
                # check is token is for same app key
                cache_data = json.load(f)
                cached_app_key = cache_data['app_key']
                if cached_app_key == self.app_key:
                    token = cache_data['token']
                    # check if token is valid
                    connection = SaxoConnection(self.environment, token)
                    connection.get_account_info()
                    # if yes, return connection
                    logging.info("Token cache found, using cached token")
                    return connection
                # fall through to interactive login
        except FileNotFoundError:
            logging.info("Token cache not found, performing interactive login")
        except Exception:
            # log exception and fall through to interactive login
            logging.warning("Token cache found, but token is invalid, performing interactive login", exc_info=True)
        # perform interactive login
        return self._run_interactive_login()

    def _run_interactive_login(self) -> SaxoConnection:
        logging.info("Performing interactive login, please follow the instructions in the browser window")
        code: str = self._authenticate_user()
        return self._exchange_code_for_token(code)

    def _authenticate_user(self) -> str:
        app: Flask = Flask(__name__)
        code: str = ''
        code_set_event: Event = threading.Event()

        @app.route('/webhook', methods=['GET'])
        def webhook():
            logging.debug(f"Got webhook with args:{request.args}")
            # Verify state matches
            if request.args['state'] != self.state:
                return "State mismatch", 400

            nonlocal code
            code = request.args['code']
            code_set_event.set()
            return "Main thread continue, please close this window", 200

        def run_server():
            app.run(port=5050)

        # Run the Flask app in a separate thread
        t = threading.Thread(target=run_server)
        t.start()
        # Open the browser
        webbrowser.open(self.auth_url)
        # Wait for the server thread to finish (e.g., after the server is shut down)
        code_set_event.wait()
        return code

    def _exchange_code_for_token(self, code: str) -> SaxoConnection:
        """Exchange authorization code for access token."""
        logging.debug(f"Exchanging code {code} for token")
        # Sending the POST request with basic authentication and
        # body as described in https://www.developer.saxo/openapi/learn/oauth-authorization-code-grant
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_url,
        }
        response = requests.post(self.token_url, data=data, auth=(self.app_key, self.app_secret))
        logging.debug(f"Token exchange response: {response.status_code} {response.content}")
        if response.status_code < 200 or response.status_code >= 300:
            raise Exception(f"Token exchange failed with status code {response.status_code}")
        # extract token
        response_json: dict = response.json()
        token: str = response_json['access_token']
        # cache token
        # ensure cache file and directory exist
        directory = os.path.dirname(self.TOKEN_CACHE_FILE)
        os.makedirs(directory, exist_ok=True)
        with open(self.TOKEN_CACHE_FILE, 'w') as f:
            json.dump({'app_key': self.app_key, 'token': token}, f)
        # return connection
        return SaxoConnection(self.environment, token)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    connection = SaxoLogin("live.json").login()
    for p in connection.get_account_positions():
        print(f"{p.name} {p.amount} {p.open_price} {p.current_price} {p.profit_loss} {p.exposure}")
    print(f"Cash={connection.get_account_balance()}")