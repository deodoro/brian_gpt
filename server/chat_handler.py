import tornado
import os
import logging
import requests
import openai
import json
import re
import uuid
import datetime
import time
import jwt

server_log = logging.getLogger('server')
chat_log = logging.getLogger('chat')

class CorsHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")

    def options(self, *args):
        self.set_header("Access-Control-Allow-Methods", "*")
        self.set_header("Access-Control-Request-Credentials", "true")
        self.set_header("Access-Control-Allow-Private-Network", "true")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_status(204)  # No Content

def save_chat_history(chat_id, chat):
    pass

class ChatHandler(CorsHandler):
    def initialize(self):
        pass

    async def fetch_jwks(self, jwks_uri):
        http_client = tornado.httpclient.AsyncHTTPClient()
        response = await http_client.fetch(jwks_uri)
        jwks = json.loads(response.body)
        return {
            key["kid"]: jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
            for key in jwks["keys"]
        }

    async def prepare(self):
        token = self.request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            self.set_status(401)
            self.finish("Missing or invalid token")
            return

        token = token.split(" ")[1]

        jwks_uri = "https://login.microsoftonline.com/common/discovery/keys"
        jwks = await self.fetch_jwks(jwks_uri)

        kid = jwt.get_unverified_header(token)["kid"]

        try:
            jwt.decode(token, jwks[kid], algorithms=['RS256'], audience=os.getenv("OAUTH_CLIENT_ID"), issuer="https://sts.windows.net/296985c5-7b22-48c1-bac3-748b5b82de20/")
        except Exception as e:
            self.set_status(401)
            self.finish(f"Invalid token: {str(e)}")
            return

    def post(self):
        try:
            chat = json.loads(self.request.body)
            chat_id = chat["chatId"]
            # temperature is normalized to 0-1.5
            # 2 is too hot, gpt35 breaks
            # temperature = req_body["temperature"] * 3 / 4
            temperature = 0.1
        except ValueError:
            server_log.error("Invalid JSON data")
            self.set_status(400)
            self.write("Invalid chat data")
            return

        try:
            openai.api_key = os.getenv("OPENAI_API_KEY")
            chatgpt_model_name = os.getenv("CHAT_MODEL") or "gpt-3.5-turbo-16k"
            chat_log.info(f"Q='{chat['chat'][-1]['content']}'")

            response = openai.ChatCompletion.create(
                model=chatgpt_model_name,
                messages=[{"role": i["role"], "content": i["content"]} for i in chat['chat']],
                temperature=temperature,
                stream = True
            )

            self.set_header("Content-Type", "text/event-stream;charset=utf-8")
            self.set_header("Cache-Control", "no-cache")

            content = ""
            for chunk in response:
                if "content" in chunk["choices"][0]["delta"]:
                    piece = chunk["choices"][0]["delta"]["content"]
                    content += piece
                    self.write(piece)
                    self.flush()

            new_item = {"role": "assistant", "content": content}

            self.write("\n\n**DONE**\n\n");
            self.write(json.dumps(new_item))

            # Create a new ShareFileClient instance for the chat history file
            # if chat_id:
            #     save_chat_history(chat_id, json.dumps({"id": chat_id, "messages": chat + [new_item]}))

        except Exception as e:
            server_log.error(e)
            self.set_status(500)
            self.write("Internal error")
