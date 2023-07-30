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
from langchain.prompts import PromptTemplate

import logging

server_logger = logging.getLogger('server')
chat_logger = logging.getLogger('chat')

# stuff_prompt_template = """You speak only in rhymes. You are Economics PhD student, the microeconomics teacher assistant. You are trying to help students to study exam questions. For each answer, expand concepts and demonstrate your knowledge. Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. Output markup in HTML.
stuff_prompt_template = """You are student in the Economics PhD, assistant for microeonomics.

Use only this information: {context}

Answer considering only the reference material: {question}

Lecture with examples and explain concepts of microeconomics related to your final answer.
"""

map_reduce_question_template = """You are student in the Economics PhD, assistant for microeonomics. Use the following portion of a long document to see if any of the text is relevant to answer the question.
When input text is relevant, lecture about the relation between question and input. Otherwise reply "No comment".

Document: {context}

Question: {question}

Comment:
"""

map_reduce_combine_template = """You are student in the Economics PhD, assistant for microeonomics.
Given the following extracted parts of a long document and a question, create a final answer.
Lecture, give examples and present and explain concepts of microeconomics contained in your final answer.

SOURCES:

QUESTION: {question}

{summaries}

FINAL ANSWER:"""

class CustomCallbackHandler(BaseCallbackHandler):
    def __init__(self, request_handler=None):
        self.request_handler = request_handler
        self.i = 0

    def on_llm_new_token(self, token, **kwargs):
        if self.request_handler:
            self.request_handler.write(token)
            self.request_handler.flush()

    # def on_llm_end(self, outputs, **kwargs):
    #     if self.request_handler:
    #         print("\n\n")
    #         self.request_handler.finish()

def perform(request_handler, query, temperature, chain, sources, retrieval_k, model, verbose, embedding_size = 350, method = 'retrieval'):
    try:
        server_logger.info(f"Running with temperature={temperature} chain={chain} sources={sources} retrieval_k={retrieval_k} model={model} method={method}")
        chat_logger.info(f"c[{chain}].Q='{query}'")

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
                collection_name=f"{collection}_{embedding_size}",
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
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        if method == 'conversation':
            qa_chain = ConversationalRetrievalChain.from_llm(
                llm,
                retriever=retriever,
                verbose=verbose,
                memory=memory,
            )
            # chat_history = []
            # input["chat_history"] = chat_history
            input["question"] = query
        else:
            if chain == "stuff":
                chain_type_kwargs = {"prompt": PromptTemplate(
                    template=stuff_prompt_template, input_variables=["context", "question"]
                )}
            elif chain == "map_reduce":
                chain_type_kwargs = {"question_prompt": PromptTemplate(
                    template=map_reduce_question_template, input_variables=["context", "question"]
                ), "combine_prompt": PromptTemplate(
                    template=map_reduce_combine_template, input_variables=["summaries", "question"]
                )}
            else:
                chain_type_kwargs = {}

            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type=chain,
                retriever=retriever,
                return_source_documents=sources,
                verbose=verbose,
                chain_type_kwargs=chain_type_kwargs,
            )
            input["query"] = query

        retval = qa_chain(input)
        return retval
    except Exception as e:
        server_logger.error(e)


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
        verbose = data.get('verbose')
        embedding_size = data.get('embedding_size')
        # Call the perform function
        self.set_header("Content-Type", "text/event-stream;charset=utf-8")
        self.set_header("Cache-Control", "no-cache")
        self.set_status(200)
        result = perform(self, query, temperature, chain, sources, k, model, verbose, embedding_size)
        self.write("\n\n**DONE**\n\n" + json.dumps(result, cls=DocumentEncoder))
