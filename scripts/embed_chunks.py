import sys
import dotenv
import os
import json
import time
import shutil
from glob import glob
from langchain.llms.openai import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
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
  tm = time.time()
  file = sys.argv[1]
  (filename, ext) = os.path.splitext(os.path.basename(file))
  print("Loading file: " + file)
  out_filename = f"output/{filename}.1{ext}"
  all_data = json.load(open(file, 'r'))
  if os.path.exists(out_filename):
    print("Loading partial: " + out_filename)
    with open(out_filename, 'r') as f:
      docs = json.load(f)
    if len([1 for item in zip(all_data,docs) if item[0]['page_content'] != item[1]['page_content']]) > 0:
      print("Partial is not consistent with input file")
      exit(1)
  else:
    docs = []

  data = all_data[len(docs):]
  embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

  c = len(docs)
  for item in data:
    c += 1
    print("Loading doc [{0}/{1}]".format(c, len(all_data)), end="\r")
    try:
      if item["page_content"]:
        embeddings.embed_query(item["page_content"])
        docs.append({**item, "embedding": embeddings.embed_query(item["page_content"])})
      else:
        raise Exception("No page content")

    except Exception as e:
      print("Error embedding document: " + str(e))
      docs.append({**item, "embedding": None})

    if os.path.exists(out_filename):
      shutil.move(out_filename, out_filename + ".bak")
    with open(out_filename, 'wt') as f:
        f.write(json.dumps(docs, indent=2))

  print("Done loading documents")
  print(f"Ellapsed: {time.time() - tm:.2f} secs")
