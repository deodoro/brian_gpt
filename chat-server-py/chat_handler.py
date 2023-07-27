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

    def post(self):
        try:
            chat = json.loads(self.request.body)
            chat_id = chat["chatId"]
            print(chat)
            # temperature is normalized to 0-1.5
            # 2 is too hot, gpt35 breaks
            # temperature = req_body["temperature"] * 3 / 4
            temperature = 0.1
        except ValueError:
            logging.error("Invalid JSON data")
            self.set_status(400)
            self.write("Invalid chat data")
            return

        try:
            openai.api_key = os.getenv("OPENAI_API_KEY")
            chatgpt_model_name = "gpt-3.5-turbo-16k"

            response = openai.ChatCompletion.create(
                model=chatgpt_model_name,
                messages=chat['chat'],
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

            self.write("**DONE**\n\n");
            self.write(json.dumps(new_item))

            # Create a new ShareFileClient instance for the chat history file
            if chat_id:
                save_chat_history(chat_id, json.dumps({"id": chat_id, "messages": chat + [new_item]}))

        except Exception as e:
            logging.error(e)
            self.set_status(500)
            self.write("Internal error")
