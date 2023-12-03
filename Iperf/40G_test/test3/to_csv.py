import csv
import re

# Path to the text file
txt_file_path = 'results.txt'

# Initialize dictionary to store data
data_dict = {}

# Read the .txt file and parse data
with open(txt_file_path, 'r') as file:
    for line in file:
        # Regular expression to extract parallel, iteration, and bandwidth
        match = re.match(r'Bandwidth for parallel=(\d+), iteration (\d+): (\d+\.\d+) Gbits/sec', line)
        if match:
            parallel = int(match.group(1))
            iteration = int(match.group(2))
            bandwidth = float(match.group(3))

            # Add bandwidth to data dictionary
            if iteration not in data_dict:
                data_dict[iteration] = [None] * 5  # Assumes parallel goes from 1 to 5
            data_dict[iteration][parallel - 1] = bandwidth

# Path to the .csv file
csv_file_path = 'data.csv'

# Write data to the .csv file
with open(csv_file_path, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Iteration', 'P1', 'P2', 'P3', 'P4', 'P5'])  # Header row
    for iteration, bandwidths in sorted(data_dict.items()):
        writer.writerow([iteration] + bandwidths)
