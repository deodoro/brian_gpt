#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
import logging
import os
import sys
import datetime
import re
import chathandler
from db_handler import *
from dotenv import load_dotenv

load_dotenv()

# Boilerplate logger setup
log_format = '%(asctime)s %(levelname)s:%(name)s:%(message)s'
date_format = '%Y-%m-%d %H:%M:%S'
logging.basicConfig(filename='server.log', level=logging.INFO,format=log_format, datefmt=date_format)
logger = logging.getLogger('server')
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter(log_format)
ch.setFormatter(formatter)
logging.getLogger('').addHandler(ch)

# class LogHandler(tornado.web.RequestHandler):
#     def get(self):
#         start = self.get_argument('start', None)
#         end = self.get_argument('end', None)
#         if re.match(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", start) and re.match(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", end):
#             self.set_header('Content-Type', 'application/json')
#             self.write(services.log(start, end))
#             self.set_status(200)
#         else:
#             self.set_status(400)

# API server boot
if __name__ == '__main__':
    try:
        logger.info('Webserver boot')

        # Associating URI handers
        cache = {}
        urls = [
            (r'/api/chat', chathandler.ChatHandler),
            (r'/api/years/?', YearsHandler),
            (r'/api/exams/(.*)', ExamsHandler),
            (r'/api/parts/(.*)/(.*)', PartsHandler),
            (r'/api/numbers/(.*)/(.*)/(.*)', NumbersHandler),
            (r'/api/questions/([^/]+)$', QuestionsByYearHandler),
            (r'/api/questions/([^/]+)/([^/]+)$', QuestionsByExamHandler),
            (r'/api/questions/([^/]+)/([^/]+)/([^/]+)/([^/]+)$', QuestionsHandler),
            (r'/api/question/(.*)', QuestionHandler),
        ]

        # Tornado initialization
        webServerPort = os.getenv('PORT') or 7071
        application = tornado.web.Application(urls, debug=False)
        application.listen(webServerPort)

        # Startup
        logger.info('Webserver is listening to port %s' % webServerPort)
        tornado.ioloop.IOLoop.instance().start()

    except Exception as e:
        logger.exception('Webserver fatal error')
