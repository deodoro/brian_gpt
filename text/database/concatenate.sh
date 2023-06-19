#!/bin/bash

output_file="output.txt"  # specify output file name
marker="\n\n---\n\n\n"  # marker between files

# remove output file if it exists
if [ -f $output_file ] ; then
    rm $output_file
fi

# list text files in current directory, sorted by name
for file in $(ls *.txt | sort)
do
    # append file content without empty lines to output file
    grep -v '^[[:space:]]*$' $file >> $output_file
    # append marker to output file
    printf $marker >> $output_file
done

