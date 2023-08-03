import dotenv
import os
from langchain.llms.openai import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings

import json
from langchain.document_loaders import TextLoader
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.pgvector import PGVector, DistanceStrategy
from langchain.docstore.document import Document

dotenv.load_dotenv()

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

if __name__ == '__main__':
    data = json.load(open('inputs/qualifiers.json', 'r'))
    docs = []

    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    def get_embeddings(text):
      if text:
          return embeddings.embed_query(text)
      else:
          return None

    c = 1
    for item in data:
        print("Loading documents... [{0}/{1}]".format(c, len(data)), end="\r")
        c += 1
        u = { "y": item["y"], \
              "q": item["q"], \
              "t": item["t"], \
              "n": item["n"], \
              "q": get_embeddings(item["q"])
        }
        docs.append(u)
        with open('output/qualifiers_embedded.json', 'wt') as f:
            f.write(json.dumps(docs, indent=2))
    print("Done loading qualifiers")

if __name__ == '__main__1':
    # test embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    print(embeddings.embed_query("a question"))

    # test comms
    llm = OpenAI()
    print(llm("what is the meaning of life?", model="gpt-4"))
