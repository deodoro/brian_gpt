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

def write_to_file(out_filename, docs):
  t = time.time()
  if os.path.exists(out_filename) and os.path.getsize(out_filename) > 0:
    shutil.move(out_filename, out_filename + ".bak")
  with open(out_filename, 'wt') as f:
    f.write(json.dumps(docs, indent=2))
  print(f"\nwritten in {(time.time() - t):.2f}")

def main():
  tm = time.time()
  file = sys.argv[1]
  (filename, ext) = os.path.splitext(os.path.basename(file))
  print("Loading file: " + file)
  out_filename = f"output/sources/{filename}.1{ext}"
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
  b = 0
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

    b += 1
    if b % 50 == 0:
      write_to_file(out_filename, docs)

  if b % 30 != 0:
    write_to_file(out_filename, docs)

  print("Done loading documents")
  print(f"Ellapsed: {time.time() - tm:.2f} secs")

if __name__ == '__main__':
  main()
