#!/bin/bash

# The file where memory usage data will be stored
output_file="memory_usage.txt"

# The number of seconds between each measurement
interval=1

# The total duration for the script to run (in seconds)
duration=60

# Initialize time elapsed
time_elapsed=0

# Clear the output file
echo "" > $output_file

# Collect data
while [ $time_elapsed -lt $duration ]; do
    # Append current memory usage to the file
    free | grep Mem | awk '{print $3}' >> $output_file
    
    # Wait for the specified interval
    sleep $interval
    
    # Update time elapsed
    let time_elapsed=$time_elapsed+$interval
done

# Calculate average memory usage
awk '{ sum += $1 } END { if (NR > 0) print sum / NR }' $output_file
