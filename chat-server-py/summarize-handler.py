import os
import io
import re
import logging
import azure.functions as func
import openai
import PyPDF2
import requests
from langchain.llms import AzureOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter

# Configure OpenAI API
chatgpt_model_name = os.getenv('CHATGPT_MODEL')
openai.api_type = "azure"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_base = os.getenv('AZURE_ENDPOINT')
openai.api_version = "2023-03-15-preview"

# Regular AzureAI class does not work with summarize + gpt35-turbo model
# https://stackoverflow.com/questions/75884448/langchain-logprobs-best-of-and-echo-parameters-are-not-available-on-gpt-35-tur
class NewAzureOpenAI(AzureOpenAI):
    @property
    def _invocation_params(self):
        params = super()._invocation_params
        params.pop('logprobs', None)
        params.pop('best_of', None)
        params.pop('echo', None)
        return params

# Summarizes Documents with langchain
def summarize(docs, temperature):
    llm = NewAzureOpenAI(openai_api_key=openai.api_key, temperature=temperature, deployment_name=os.getenv('CHATGPT_MODEL'), max_tokens=4000)
    chain = load_summarize_chain(llm, chain_type="map_reduce")
    return chain.run(docs)

# Extracts text from PDF and returns text split (Documents)
def extract_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        s = re.sub(r'[^\x20-\x7E\n]', '', page.extract_text())
        s = re.sub(r'(.)\1+', r'\1', s)
        text = text + s + '\n\n'

    text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    texts = text_splitter.split_text(text)

    return [Document(page_content=t) for t in texts[:3]]

# Downloads PDF from URL and returns Documents
def read_pdf(url):
    response = requests.get(url, allow_redirects=True)
    bytes = io.BytesIO(response.content)
    return extract_pdf(bytes)

def main(req: func.HttpRequest) -> func.HttpResponse:
    url = req.params.get('url')
    temperature = req.params.get('temperature')

    # check if 'temperature' is empty or missing, if so, set it to 0
    if not temperature:
        temperature = 0
    else:
        try:
            # try to convert the temperature to a float value
            temperature = float(temperature)
        except ValueError:
            return func.HttpResponse(
                "Invalid temperature value. Please provide a valid number.",
                status_code=400
            )

    if url:
        return func.HttpResponse(summarize(read_pdf(url), temperature))
    else:
        return func.HttpResponse(
            "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
            status_code=200
        )
