import os
import json
import re
import argparse

def concatenate_short_pages(lines):
    i = 0
    intermediate = []
    while i < len(lines) - 1:
        if len(lines[i]) < 150:
            text = lines[i]
            i = i + 1
            while i < len(lines) - 1 and len(lines[i]) < 150:
                text += ' ' + lines[i]
                i = i + 1
            intermediate.append(text)
        else:
            intermediate.append(lines[i])
            i = i + 1
    i = 0
    output = []
    while i < len(intermediate) - 1:
        if len(intermediate[i]) < 150:
            text = intermediate[i]
            i = i + 1
            output.append(text + ' ' + intermediate[i])
            i = i + 1
        else:
            output.append(intermediate[i])
            i = i + 1
    return output

def process_file_contents(file_contents):
    # Remove trailing spaces
    file_contents = file_contents.strip()

    # Replace single newline with space
    file_contents = re.sub(r'(?<!\n)\n(?!\n)', ' ', file_contents)

    file_contents = re.sub(r'\[(.*?)\]', r'\1', file_contents)

    file_contents = re.sub(r'(?<!\n)\n(?!\n)', ' ', file_contents)

    # Replace multiple newlines with a single newline
    file_contents = re.sub(r'\n+', '\n', file_contents)

    # Split into pages at every newline
    pages = file_contents.split('\n')

    pages = [re.sub(r"\s+", " ", p) for p in pages]



    # Remove any blank pages
    pages = [p.strip() for p in pages if p.strip() != '']

    return concatenate_short_pages(pages)

def main(input_directory):
    lecture_files = [f for f in os.listdir(input_directory) if os.path.isfile(os.path.join(input_directory, f)) and f.endswith('.txt')]

    lectures = []

    for lecture_file in lecture_files:
        # get lecture info from file name
        name_parts = lecture_file.split('-')
        number = name_parts[0]
        title = ' '.join(name_parts[1:]).replace('.txt', '').replace('-', ' ').title()

        # open file and read contents
        with open(os.path.join(input_directory, lecture_file), 'r') as f:
            file_contents = f.read()

        pages = process_file_contents(file_contents)

        # build JSON structure for lecture
        lecture = {
            "title": title,
            "pages": [{"content": p, "number": i+1} for i, p in enumerate(pages)]
        }

        lectures.append(lecture)

    # output JSON for all lectures
    with open('website.json', 'w') as f:
        json.dump(lectures, f, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process text files in a directory into a structured JSON format.')
    parser.add_argument('input_directory', type=str, help='The directory containing the text files to process.')

    args = parser.parse_args()

    main(args.input_directory)
