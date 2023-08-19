import sys
import os
import json
import argparse
from langchain.text_splitter import SpacyTextSplitter
from glob import glob

def remove_single_word_lines(text):
    lines = text.split('\n\n')
    new_lines = [line for line in lines if len(line.split()) > 1]
    return '\n\n'.join(new_lines)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('chunk_size', type=int, help='Size of the text chunks.')
    args = parser.parse_args()

    chunk_size = args.chunk_size
    # chunk_overlap = int(chunk_size * 0.10)  # 10% of chunk_size
    text_splitter = SpacyTextSplitter(chunk_size=chunk_size, chunk_overlap=0)

    docs = []
    for file in glob('inputs/*.json'):
        if file != 'inputs/questions_db.json' and file != 'inputs/qualifiers.json':
            filename = os.path.basename(file)
            print("Loading file: " + file, end="")
            sys.stdout.flush()
            data = json.load(open(file, 'r'))
            metadatas = []

            for item in data:
                title = item["title"] if "title" in item else ""
                author = item["author"] if "author" in item else ""
                _type = item["type"] if "type" in item else ""
                ref = item["ref"] if "ref" in item else ""
                base_metadata = { \
                        "title": title, \
                        "author": author, \
                        "type": _type, \
                        "ref": ref}
                metadatas = [{**base_metadata, "page_number": i["number"]} for i in item["pages"]]
                docs += text_splitter.create_documents([i["content"] for i in item["pages"]], metadatas)
            print("\r  Split file: " + file)

    output_filename = f'output/chunked_{chunk_size}.json'
    with open(output_filename, 'wt') as f:
        json.dump([{"page_content": remove_single_word_lines(d.page_content), "metadata": d.metadata} for d in docs], f, indent=1)
