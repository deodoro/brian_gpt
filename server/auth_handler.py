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
        body = urlencode({
            "client_id": os.getenv("OAUTH_CLIENT_ID"),
            "redirect_uri": os.getenv("OAUTH_REDIRECT_URI"),
            "client_secret": os.getenv("OAUTH_CLIENT_SECRET"),
            "code": code,
            "grant_type": "authorization_code"
        })
        server_log.info(f"KEY={os.getenv('OAUTH_TOKEN_URI')}")

        response = await http_client.fetch(os.getenv("OAUTH_TOKEN_URI"), method="POST", body=body)
        tokens = json.loads(response.body)

        # Here, tokens should have your access_token and optionally a refresh_token
        access_token = tokens.get("access_token")

        if not access_token:
            self.write("Error: No access token received.")
            return

        # (Optional) Fetch user profile or other details if needed

        # Set up your own method of recognizing this user. For instance, set a cookie or session.
        self.set_secure_cookie("user", access_token)  # this is just a simple example

        self.redirect("/")  # Redirect back to the main application


#OAUTH_CLIENT_ID="98c81f0b-a22a-4b8c-82c1-962e998bb386"
