import csv
import re

# Prepare the data
data_dict = {}
with open('combined_output.txt', 'r') as file:
    for line in file:
        p_value = int(re.search(r'(?<=P=)\d+', line).group())
        iteration = int(re.search(r'(?<=iteration )\d+', line).group())
        bandwidth = float(re.search(r'\d+\.\d+(?= Mbits/sec)', line).group())

        if p_value not in data_dict:
            data_dict[p_value] = {}

        data_dict[p_value][iteration] = bandwidth

# Create the csv
max_iterations = max(max(inner.keys()) for inner in data_dict.values())
header = ['Iteration'] + [f'P={p_value}' for p_value in sorted(data_dict.keys())]

with open('output.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(header)
    for i in range(1, max_iterations+1):
        row = [i] + [data_dict[p_value].get(i, '') for p_value in sorted(data_dict.keys())]
        writer.writerow(row)
