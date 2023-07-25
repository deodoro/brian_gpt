import os
import json

# get list of all text files
lecture_files = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.txt')]

lectures = []

for lecture_file in lecture_files:
    # get lecture info from file name
    name_parts = lecture_file.split('-')
    number = name_parts[1]
    year = name_parts[2]
    month = name_parts[3]
    day = name_parts[4].split('.')[0] # removing .txt extension

    # open file and read lines
    with open(lecture_file, 'r') as f:
        lines = f.read().splitlines()

    # split lines into pages of 200 lines each
    pages = [" ".join(lines[i:i + 200]) for i in range(0, len(lines), 200)]

    # build JSON structure for lecture
    lecture = {
        "title": "Lecture on " + month + "-" + day + "-" + year,
        "pages": [{"content": p, "number": i+1} for i, p in enumerate(pages)]
    }

    lectures.append(lecture)

# output JSON for all lectures
with open('lectures.json', 'w') as f:
    json.dump(lectures, f, indent=2)
