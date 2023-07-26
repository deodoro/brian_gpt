import sys
import dotenv
import os
import psycopg
import json
import openai
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

# from langchain.llms import AzureOpenAI

# class NewAzureOpenAI(AzureOpenAI):
#     @property
#     def _invocation_params(self):
#         params = super()._invocation_params
#         # params.pop('logprobs', None)
#         # params.pop('best_of', None)
#         # params.pop('echo', None)
#         return params

if __name__ == "__main__":
    dotenv.load_dotenv()
    # llm = ChatOpenAI(temperature = 0.2, model = 'gpt-3.5-turbo-16k')

    azure_deployment_name = "gpt-35-turbo-16k"
    azure_model_name = "gpt-35-turbo-16k"

    openai.api_type = "azure"
    openai.api_key = os.getenv("AZURE_OPENAI_KEY")
    openai.api_base = os.getenv('AZURE_ENDPOINT')
    openai.api_version = "2023-06-01-preview"

    # llm = NewAzureOpenAI(
    #     openai_api_type = "azure",
    #     openai_api_key = os.getenv("AZURE_OPENAI_KEY"),
    #     openai_api_base = os.getenv('AZURE_ENDPOINT'),
    #     openai_api_version = "2023-06-01-preview",
    #     model=  os.getenv("AZURE_MODEL"),
    #     model_kwargs = { "engine": "test2" },
    #     temperature = 0,
    # )

    with open("output/questions_embedded.json", "r") as f:
        questions = json.load(f)
    out = []
    i = 0
    for q in questions:
        i += 1
        print("Processing {0}/{1}".format(i, len(questions)), end="\r")
        query = f"A question from a PhD microeconomics exam follows. Write 10 search tags that one can use for filters. Good tags are generic dictionary words. Output words separated by comma. Do not use any of the following tags nor similar: microeconomics, player 1, p_x, p_y, p(a|b),p(a),PhD exam,Kreps figure 12.11(a).\n\nquestion\n\n{q['combined']}"
        response = openai.ChatCompletion.create(
                engine="gpt-35-turbo-16k", # replace this value with the deployment name you chose when you deployed the associated model.
                messages = [{"role":"system","content":"You are an economics teacher assistant. You only provide factual answers to queries, and do not provide answers that are not related economics."},{"role":"user","content":query}],
                temperature=0,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None)
        tags = response.choices[0]["message"]["content"]
        query = f"Sort from better to worst the tags for this question. remove irrelevant tags. output tags separated by comma.\n\nquestion\n\n{q['combined']}\n\ntags\n\n{tags}"
        rerank = openai.ChatCompletion.create(
                engine="gpt-35-turbo-16k", # replace this value with the deployment name you chose when you deployed the associated model.
                messages = [{"role":"system","content":"You are an economics teacher assistant. You only provide factual answers to queries, and do not provide answers that are not related economics."},{"role":"user","content":query}],
                temperature=0,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None)
        retags = rerank.choices[0]["message"]["content"]
        out.append({**q, 'tags': [i.strip() for i in retags.split(',')]})
    with open("output/questions_tagged.json", "w") as f:
        json.dump(out, f, indent=2)
