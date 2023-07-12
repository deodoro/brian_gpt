# Standard library imports
import os
import re
import json
import dotenv
import shutil
from glob import glob
from pathlib import Path

# External library imports
import openai

# Local imports
from langchain.llms import AzureOpenAI
from langchain.llms.openai import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings

# Load environment variables
dotenv.load_dotenv("./.env_gp4")


# Set OpenAI configuration
openai.api_type = "azure"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_base = os.getenv('AZURE_ENDPOINT')
openai.api_version = "2023-03-15-preview"

# Test Chat
messages=[
    {"role": "user", "content": "What is azure cognitive services?"}
]

# Print chat completion result
print(openai.ChatCompletion.create(
        engine="test-32k",
        model="gpt4-32k",
        messages=messages)["choices"][0]["message"]["content"])
