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
    data = json.load(open('inputs/question_db.json', 'r'))
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
        answer = item["answer"].replace('[ChatGPT]', '').strip()
        explanation = item["explanation"].replace('[ChatGPT]', '').strip()
        u = { "enunciate": item["enunciate"], \
            "answer": answer, \
            "explanation": explanation, \
            "combined" : format_response(item["enunciate"], answer, explanation),
            "embedding_enunciate": get_embeddings(item["enunciate"]),\
            "embedding_answer": get_embeddings(answer),\
            "embedding_explanation": get_embeddings(explanation),\
            "embedding_combined": get_embeddings(format_response(item["enunciate"], answer, explanation))}
        docs.append(u)
        with open('output/questions_embedded.json', 'wt') as f:
            f.write(json.dumps(docs, indent=2))
    print("Done loading documents")

if __name__ == '__main__1':
    # test embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    print(embeddings.embed_query("a question"))

    # test comms
    llm = OpenAI()
    print(llm("what is the meaning of life?", model="gpt-4"))
