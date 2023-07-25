import sys
import pdftotext
import json
import PyPDF2
import os
import re
import argparse

DISCLAIMER = r"\s*(This content downloaded.+)$"

def cleanup(pages, args):
    if args.f:
        pages = pages[1:]
    if args.s:
        pages = [re.sub(r"-\s\n\s", "", p) for p in pages]
    if args.n:
        pages = [p.replace("\n", " ") for p in pages]
    if args.r:
        pages = [re.sub(r"\s+", " ", p) for p in pages]
    if args.a:
        pages = [re.sub(r"[^\x00-\x7F]+", " ", p) for p in pages]
    if args.b:
        pages = [re.sub(r'\[(.*?)\]', r'\1', p) for p in pages]
    if args.d:
        pages = [re.sub(DISCLAIMER, "", p.strip(), re.MULTILINE) for p in pages]
    return pages

def extract_text_from_pdf_pypdf(file_name):
    with open(file_name, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        try:
            title = pdf_reader.metadata['/Title']
        except:
            title = ""
        pages = []
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            if text:
                pages.append(text)
    return (title, pages)

def extract_text_from_pdf_pdftotext(file_name):
    with open(file_name, 'rb') as file:
        pdf = pdftotext.PDF(file)
    return ('', [page for page in pdf if page.strip() != ''])

def save_to_text_file(title, pages, output_file):
    with open(output_file, 'w') as file:
        o = {"title": title, "pages": [{"content": p, "number": i} for i,p in enumerate(pages,1)]}
        file.write(json.dumps(o, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input_pdf_file', type=str, help="Input PDF file")
    parser.add_argument('output_json_file', type=str, nargs='?', default=None, help="Output JSON file")
    parser.add_argument('-f', action='store_true', help="Remove first page")
    parser.add_argument('-s', action='store_true', help="Remove hyphenization")
    parser.add_argument('-n', action='store_true', help="Replace newlines with spaces")
    parser.add_argument('-r', action='store_true', help="Remove repeated spaces")
    parser.add_argument('-a', action='store_true', help="Remove non-ascii characters")
    parser.add_argument('-b', action='store_true', help="Remove brackets")
    parser.add_argument('-d', action='store_true', help="Remove disclaimer")
    parser.add_argument('-p', action='store_true', help="Use pdftotext instead of PyPDF2")
    args = parser.parse_args()

    if args.output_json_file is None:
        [fname, fext] = os.path.splitext(args.input_pdf_file)
        output_file = fname + ".json"
    else:
        output_file = args.output_json_file

    if args.p:
        f = extract_text_from_pdf_pdftotext
    else:
        f = extract_text_from_pdf_pypdf
    (title, extracted_text) = f(args.input_pdf_file)
    extracted_text = cleanup(extracted_text, args)
    save_to_text_file(title, extracted_text, output_file)
