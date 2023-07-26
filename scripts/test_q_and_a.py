import sys
import dotenv
import os
import argparse
import psycopg
import json
from langchain.llms import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.pgvector import PGVector, DistanceStrategy
from langchain.retrievers import ContextualCompressionRetriever
from langchain.chat_models import ChatOpenAI
from langchain.retrievers.document_compressors.chain_extract import LLMChainExtractor
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.retrievers.merger_retriever import MergerRetriever
from IPython.display import Markdown, display
from langchain.callbacks.base import BaseCallbackHandler
from langchain.memory import ConversationBufferMemory

class MyCustomHandlerOne(BaseCallbackHandler):
    def on_llm_new_token(self, token, **kwargs):
        print(token, end="")
        sys.stdout.flush()

    def on_llm_end(self, outputs, **kwargs):
        print("\n\n")

def perform(text, temperature, chain, sources, retrieval_k, model, method):
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
            collection_name=collection + "_1500",
        )
        retrievers.append(db.as_retriever(search_kwargs={"k": retrieval_k}))

    base_retriever = MergerRetriever(retrievers=retrievers)
    llm = ChatOpenAI(temperature = temperature, model = model, callbacks=[MyCustomHandlerOne()], streaming=True)

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
        qa_chain = ConversationalRetrievalChain.from_llm(llm, retriever=retriever, verbose=False, memory=memory)
        # chat_history = []
        # input["chat_history"] = chat_history
        input["question"] = text
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
        input["query"] = text

    retval = qa_chain(input)
    return retval

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('text', type=str, help='The text to be processed.')
    parser.add_argument('-t', '--temperature', type=float, default=0.5, help='Temperature for the LLM.')
    parser.add_argument('-c', '--chain', type=str, default='stuff', help='The type of chain to use.')
    parser.add_argument('-s', '--sources', action='store_true', help='Return sources in the output.')
    parser.add_argument('-k', '--retrieval_k', type=int, default=5, help='Quantity of documents to retrieve.')
    parser.add_argument('-m', '--model', type=str, default='gpt-3.5-turbo-16k', help='AI model name.')
    parser.add_argument('-n', '--method', type=str, default='retrieval', help='The method to use. Options are retrieval_qa, compressed.')
    args = parser.parse_args()

    print(perform(args.text, args.temperature, args.chain, args.sources, args.retrieval_k, args.model, args.method))
