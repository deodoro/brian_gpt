from tornado.httpclient import HTTPError
import tornado.escape
import tornado.httpclient
import json
import os
from urllib.parse import urlencode
import logging
from dotenv import load_dotenv

load_dotenv()

server_log = logging.getLogger('server')

class AuthHandler(tornado.web.RequestHandler):
    async def get(self):
        # Get the authorization code from the query parameters
        code = self.get_argument("code", None)
        if not code:
            self.write("Error: No code provided.")
            return

        # Exchange the authorization code for an access token
        http_client = tornado.httpclient.AsyncHTTPClient()
        a = {
            "client_id": os.getenv("OAUTH_CLIENT_ID"),
            "redirect_uri": os.getenv("OAUTH_REDIRECT_URI"),
            "client_secret": os.getenv("OAUTH_CLIENT_SECRET"),
            "code": code,
            "grant_type": "authorization_code"
        }
        body = urlencode({
            "client_id": os.getenv("OAUTH_CLIENT_ID"),
            "redirect_uri": os.getenv("OAUTH_REDIRECT_URI"),
            "client_secret": os.getenv("OAUTH_CLIENT_SECRET"),
            "code": code,
            "grant_type": "authorization_code"
        })

        try:
            response = await http_client.fetch(os.getenv("OAUTH_TOKEN_URI"), method="POST", body=body)
            tokens = json.loads(response.body)
        except HTTPError as http_error:
            # Log details if it's an HTTPError
            server_log.error(f"HTTP Error. Status Code: {http_error.response.code}")
            server_log.error(f"HTTP Reason: {http_error.response.reason}")
            for header, value in http_error.response.headers.items():
                server_log.error(f"{header}: {value}")
            server_log.error(f"Body: {http_error.response.body.decode('utf-8')}")  # Assuming the body is in UTF-8 format
        except Exception as e:
            server_log.error(f"An unexpected error occurred: {e}")
        # Here, tokens should have your access_token and optionally a refresh_token
        access_token = tokens.get("access_token")

        if not access_token:
            self.write("Error: No access token received.")
            return

        self.set_secure_cookie("user", access_token, httponly=True, secure=True, samesite='Lax')
        self.write("FINE")
