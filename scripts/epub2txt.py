import ebooklib
import sys
import pdftotext
from ebooklib import epub
from bs4 import BeautifulSoup

BLACKLIST = ['[document]','noscript', 'header','html', 'meta', 'head','input', 'script',]

def epub2html(epub_path):
    book = epub.read_epub(epub_path)
    chapters = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            chapters.append(item.get_content())
    return chapters

def chap2text(text):
    output = ''
    soup = BeautifulSoup(text, 'html.parser')
    text = soup.find_all(text=True)
    for t in text:
        if t.parent.name not in BLACKLIST:
            output += '{} '.format(t)
    return output

def remove_html_markup(lines):
    Output = []
    for html in lines:
        text =  chap2text(html)
        Output.append(text)
    return '\n'.join(Output)

def save_to_text_file(text, output_file):
    with open(output_file, 'w') as file:
        file.write(text)

if __name__ == "__main__":
    input_pdf_file = sys.argv[1]
    output_text_file = sys.argv[2]
    extracted_html = epub2html(input_pdf_file)
    extracted_text = remove_html_markup(extracted_html)
    save_to_text_file(extracted_text, output_text_file)
