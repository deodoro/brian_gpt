#!/bin/bash

# Directory path
dir_path=$1

# Loop over all files in the directory
for file in "$dir_path"/*
do
    # Replace non-printable characters with spaces and remove repeated spaces
    tr -cd '[:print:]\n' < "$file" | sed 's/  */ /g' | awk 'NF' > "${file}_clean"
done

