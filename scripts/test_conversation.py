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
dotenv.load_dotenv()

# Set OpenAI configuration
openai.api_key = os.getenv("OPENAI_API_KEY")

# Test Chat
messages=[
    {"role": "user", "content": "Explain a random topic about quantum physics."},
]

# Print chat completion result
print(openai.ChatCompletion.create(
        # model="gpt-4",
        model="gpt-3.5-turbo-16k",
        messages=messages)["choices"][0]["message"]["content"])
