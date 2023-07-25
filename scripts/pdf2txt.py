import sys
import pdftotext

def extract_text_from_pdf(file_name):
    with open(file_name, 'rb') as file:
        pdf = pdftotext.PDF(file)
        return "\n\n".join(pdf)

def save_to_text_file(text, output_file):
    with open(output_file, 'w') as file:
        file.write(text)

if __name__ == "__main__":
    input_pdf_file = sys.argv[1]
    output_text_file = sys.argv[2]
    extracted_text = extract_text_from_pdf(input_pdf_file)
    save_to_text_file(extracted_text, output_text_file)
