import dotenv
import os
import json
from langchain.llms.openai import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import TextLoader
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.pgvector import PGVector, DistanceStrategy
from langchain.docstore.document import Document
from glob import glob

dotenv.load_dotenv()

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

def format_response(enunciate, answer, explanation):
  if answer and explanation:
    if answer.upper() == "TRUE":
      return enunciate + "\n\nTrue. " + explanation
    elif answer.upper() == "FALSE":
      return enunciate + "\n\nFalse. " + explanation
    else:
      return enunciate + "\n\n" + answer + ". " + explanation
  elif answer:
    return enunciate + "\n\n" + answer
  elif explanation:
    return enunciate + "\n\n" + explanation
  else:
    return None

if __name__ == '__main__':
  t = 0
  for file in glob('inputs/*.json'):
    if file != 'inputs/question_db.json':
      data = json.load(open(file, 'r'))
      for item in data:
        t += len(item["pages"])

  tt = 0

  for file in glob('inputs/*.json'):
    if file != 'inputs/question_db.json':
      filename = os.path.basename(file)
      print("Loading file: " + file)
      data = json.load(open(file, 'r'))
      docs = []

      embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
      def get_embeddings(text):
        if text:
            return embeddings.embed_query(text)
        else:
            return None

      c = 0
      for item in data:
        title = item["title"] if "title" in item else ""
        author = item["author"] if "author" in item else ""
        _type = item["type"] if "type" in item else ""
        ref = item["ref"] if "ref" in item else ""
        doc = { "title": title, \
                "author": author, \
                "type": _type, \
                "ref": ref, \
                "pages": []}
        docs.append(doc)
        p = 1
        c += 1
        for page in item["pages"]:
          print("Loading document [{0}/{1}] Page [{2}/{3}] Total [{4}/{5}]".format(c, len(data), p, len(item["pages"]), tt, t), end="\r")
          p += 1
          tt += 1
          answer = page["content"]
          u = { "content": page["content"], \
                "number": page["number"], \
                "embedding": get_embeddings(page["content"])}
          doc["pages"].append(u)

          with open(f'output/{filename}', 'wt') as f:
              f.write(json.dumps(docs, indent=2))

      print("Done loading file: " + file)

  print("Done loading documents")
