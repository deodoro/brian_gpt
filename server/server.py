#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
import logging
import os
import sys
import datetime
import re
import secrets
from chat_handler import ChatHandler
from db_handler import *
from qa_handler import QAHandler
from auth_handler import AuthHandler
from search_handler import SearchHandler
from dotenv import load_dotenv

load_dotenv()

log_format = '%(asctime)s %(levelname)s:%(name)s:%(message)s'
date_format = '%Y-%m-%d %H:%M:%S'

# Create server logger
server_logger = logging.getLogger('server')
server_logger.setLevel(logging.INFO)

# Create chat logger
chat_logger = logging.getLogger('chat')
chat_logger.setLevel(logging.INFO)

# Create console handler with a higher log level
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
ch.setFormatter(logging.Formatter(log_format, datefmt=date_format))

# Add console handler to both loggers
server_logger.addHandler(ch)
chat_logger.addHandler(ch)

# Create file handler which logs even debug messages
fh = logging.FileHandler('/var/log/app/server.log')
fh.setLevel(logging.INFO)
fh.setFormatter(logging.Formatter(log_format, datefmt=date_format))
server_logger.addHandler(fh)  # Add file handler to server logger

# Create another file handler for the 'chats.log' file
fh2 = logging.FileHandler('/var/log/app/chats.log')
fh2.setLevel(logging.INFO)
fh2.setFormatter(logging.Formatter(log_format, datefmt=date_format))
chat_logger.addHandler(fh2)  # Add file handler to chat logger

# API server boot
if __name__ == '__main__':
    try:
        server_logger.info('Webserver boot')

        # Associating URI handers
        cache = {}
        urls = [
            (r'/api/chat', ChatHandler),
            (r'/api/years/?', YearsHandler),
            (r'/api/exams/(.*)', ExamsHandler),
            (r'/api/parts/(.*)/(.*)', PartsHandler),
            (r'/api/numbers/(.*)/(.*)/(.*)', NumbersHandler),
            (r'/api/questions/([^/]+)$', QuestionsByYearHandler),
            (r'/api/questions/([^/]+)/([^/]+)$', QuestionsByExamHandler),
            (r'/api/questions/([^/]+)/([^/]+)/([^/]+)/([^/]+)$', QuestionsHandler),
            (r'/api/question/(.*)', QuestionHandler),
            (r'/api/qa', QAHandler),
            (r'/api/search', SearchHandler),
            (r'/api/auth', AuthHandler),
            (r"/()", tornado.web.StaticFileHandler, {"path": '/var/www', "default_filename": "index.html"}),
            (r"/(.*)", tornado.web.StaticFileHandler, {"path": '/var/www'}),
        ]

        # Tornado initialization
        webServerPort = os.getenv('PORT') or 7071
        application = tornado.web.Application(urls, cookie_secret=secrets.token_hex(32), debug=True)
        application.listen(webServerPort)

        # Startup
        server_logger.info('Chat model: %s' % (os.getenv("CHAT_MODEL") or "gpt-3.5-turbo-16k"))
        server_logger.info('Webserver is listening to port %s' % webServerPort)
        tornado.ioloop.IOLoop.instance().start()

    except Exception as e:
        logger.exception('Webserver fatal error')
