import tornado.escape
from tornado.web import RequestHandler
import sys
import dotenv
import os
import json
import time
from langchain.llms import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.pgvector import PGVector, DistanceStrategy
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.merger_retriever import MergerRetriever
from langchain.schema import Document

import logging

server_logger = logging.getLogger('server')
chat_logger = logging.getLogger('chat')


def perform(request_handler, query, retrieval_k, ref_type='all', embedding_size = 350):
    try:
        chat_logger.info(f"search.Q='{query}' k={retrieval_k} embedding_size={embedding_size}")

        dotenv.load_dotenv()
        connection_string = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_DATABASE')}"

        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

        if ref_type == 'all':
            retrievers = []
            for collection in ['paper', 'book', 'blog', 'lecture', 'notes']:
                db = PGVector(
                    embedding_function=embeddings,
                    connection_string=connection_string,
                    collection_name=f"{collection}_{embedding_size}",
                )
                retrievers.append(db.as_retriever(search_kwargs={"k": retrieval_k}))
            retriever = MergerRetriever(retrievers=retrievers)
            server_logger.info("retriever")
        else:
            db = PGVector(
                embedding_function=embeddings,
                connection_string=connection_string,
                collection_name=f"{ref_type}_{embedding_size}",
            )
            retriever = db.as_retriever(search_kwargs={"k": retrieval_k})

        docs = retriever.get_relevant_documents(query)
        server_logger.info(docs)
        return docs
    except Exception as e:
        server_logger.error(e)


class DocumentEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Document):
            return {'page_content': obj.page_content, 'metadata': obj.metadata}
        return super().default(obj)

class SearchHandler(RequestHandler):
    def post(self):
        # Parse JSON from request body
        data = tornado.escape.json_decode(self.request.body)

        # Extract parameters from the data
        query = data.get('query')
        k = data.get('k')
        ref_type = data.get('ref_type')
        embedding_size = data.get('embedding_size')
        # Call the perform function
        self.set_header("Content-Type", "application/json")
        self.set_header("Cache-Control", "no-cache")
        self.set_status(200)
        self.write(json.dumps(perform(self, query, k, ref_type, embedding_size), cls=DocumentEncoder))
