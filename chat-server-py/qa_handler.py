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
from langchain.chat_models import ChatOpenAI
from langchain.retrievers.document_compressors.chain_extract import LLMChainExtractor
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.retrievers.merger_retriever import MergerRetriever
from langchain.callbacks.base import BaseCallbackHandler, AsyncCallbackHandler
from langchain.memory import ConversationBufferMemory
from langchain.schema import Document
from tornado.ioloop import IOLoop

class CustomCallbackHandler(BaseCallbackHandler):
    def __init__(self, request_handler=None):
        self.request_handler = request_handler
        self.i = 0

    def on_llm_new_token(self, token, **kwargs):
        if self.request_handler:
            print("({0})token: {1}".format(self.i, token))
            self.i += 1
            IOLoop.current().add_callback(self.write_and_flush, token)

    def write_and_flush(self, token):
        self.request_handler.write(token)
        self.request_handler.flush()

    # def on_llm_end(self, outputs, **kwargs):
    #     if self.request_handler:
    #         print("\n\n")
    #         self.request_handler.finish()

def perform(request_handler, query, temperature, chain, sources, retrieval_k, model, method = 'retrieval'):

    print(f"Running with temperature={temperature} chain={chain} sources={sources} retrieval_k={retrieval_k} model={model} method={method}")

    dotenv.load_dotenv()
    connection_string = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_DATABASE')}"

    if (os.path.exists("cache.json")):
        with open("cache.json", "r") as f:
            cache = json.load(f)
    else:
        cache = {}

    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

    retrievers = []
    for collection in ['paper', 'book', 'blog', 'lecture', 'notes']:
        db = PGVector(
            embedding_function=embeddings,
            connection_string=connection_string,
            collection_name=collection + "_350",
        )
        retrievers.append(db.as_retriever(search_kwargs={"k": retrieval_k}))

    base_retriever = MergerRetriever(retrievers=retrievers)
    llm = ChatOpenAI(temperature = temperature, model = model, callbacks=[CustomCallbackHandler(request_handler)], streaming=True)

    if method == 'compressed':
        base_compressor = LLMChainExtractor.from_llm(llm)
        retriever = ContextualCompressionRetriever(base_compressor=base_compressor, base_retriever=base_retriever)
    elif method == 'retrieval' or method == 'conversation':
        retriever = base_retriever
    else:
        raise ValueError(f"Unknown method: {method}")

    input = {}
    if method == 'conversation':
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm,
            retriever=retriever,
            verbose=True,
            memory=memory,
        )
        # chat_history = []
        # input["chat_history"] = chat_history
        input["question"] = query
    else:
        memory = None
        if sources:
            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type=chain,
                retriever=retriever,
                return_source_documents=True,
                verbose=False,
            )
        else:
            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type=chain,
                retriever=retriever,
                verbose=False,
            )
        input["query"] = query

    retval = qa_chain(input)
    return retval


class DocumentEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Document):
            return {'page_content': obj.page_content, 'metadata': obj.metadata} 
        return super().default(obj)

class QAHandler(RequestHandler):
    def post(self):
        # Parse JSON from request body
        data = tornado.escape.json_decode(self.request.body)

        # Extract parameters from the data
        query = data.get('query')
        temperature = data.get('temperature')
        chain = data.get('chain')
        sources = data.get('sources')
        k = data.get('k')
        model = data.get('model')

        # Call the perform function
        self.set_header("Content-Type", "text/event-stream;charset=utf-8")
        self.set_header("Cache-Control", "no-cache")
        self.set_status(200)
        result = perform(self, query, temperature, chain, sources, k, model)
        self.write("\n\n**DONE\n\n" + json.dumps(result, cls=DocumentEncoder))
