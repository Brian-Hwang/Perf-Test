#!/bin/bash

# Get the script's directory
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Set the input file name
input_file_name="combined_output.txt"

# Create the full input file path
input_file="${script_dir}/${input_file_name}"

# Extract the base name and extension from the input file
base_name=$(basename $input_file)
name="${base_name%.*}"

# Create the output file path
output_file="${script_dir}/${name}.csv"

# Prepare temporary file
tmp_file="${script_dir}/${name}_tmp.txt"

# Parse the file and extract data
awk '{print $4 "," $6 "," $7}' $input_file | sed 's/://g' | sed 's/,//g' > $tmp_file

# Create a CSV file
echo "P_Value,Iteration,Bandwidth (Mbits/sec)" > $output_file
cat $tmp_file >> $output_file

# Remove temporary file
rm $tmp_file

echo "Output written to $output_file"

