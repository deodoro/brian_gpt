import os
import re

# Function to remove time markers and line numbers
def clean_srt(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    clean_lines = []
    for line in lines:
        # Remove time markers
        if '-->' in line:
            continue
        # Remove line numbers (assuming they are less than 10000)
        if re.match(r'^\d{1,4}$', line.strip()):
            continue
        # Append cleaned line
        clean_lines.append(line)

    return clean_lines

# Directories to process
dirs = ["./2017", "./2018"]

# Process each directory
for dir in dirs:
    for filename in os.listdir(dir):
        if filename.endswith('.srt'):
            file_path = os.path.join(dir, filename)
            clean_lines = clean_srt(file_path)

            # Output file with '_clean' suffix
            output_file_path = os.path.join(dir, f"{os.path.splitext(filename)[0]}_clean.txt")
            with open(output_file_path, 'w') as output_file:
                output_file.writelines(clean_lines)
