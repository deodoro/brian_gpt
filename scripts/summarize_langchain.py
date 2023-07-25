import sys
import dotenv
import openai
import os
import re
import shutil
import json
from pathlib import Path
from glob import glob
from langchain.llms import AzureOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter

dotenv.load_dotenv("./.env_gp")

azure_deployment_name = os.getenv('AZURE_DEPLOYMENT')
azure_model_name = os.getenv('AZURE_MODEL')

openai.api_type = "azure"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_base = os.getenv('AZURE_ENDPOINT')
openai.api_version = "2023-03-15-preview"

class NewAzureOpenAI(AzureOpenAI):
    @property
    def _invocation_params(self):
        params = super()._invocation_params
        params.pop('logprobs', None)
        params.pop('best_of', None)
        params.pop('echo', None)
        return params

llm = NewAzureOpenAI(
    openai_api_type = "azure",
    openai_api_key = os.getenv("AZURE_OPENAI_KEY"),
    openai_api_base = os.getenv('AZURE_ENDPOINT'),
    openai_api_version = "2023-03-15-preview",
    model=  os.getenv("AZURE_MODEL"),
    model_kwargs = { "engine": os.getenv("AZURE_DEPLOYMENT") },
)

def summarize(text):
    text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    texts = text_splitter.split_text(text)
    docs = [Document(page_content=t) for t in texts[:3]]

    chain = load_summarize_chain(llm, chain_type="map_reduce")
    return chain.run(docs)

if __name__ == "__main__":
    text = open(sys.argv[1], 'r').read()
    print(summarize(text))
