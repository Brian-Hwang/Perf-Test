#!/bin/bash

# IP address
IP="20.0.1.4"

# Time 
TIME="60"

# Window size
WINDOW_SIZE="2m"

# Base directory for output files
BASE_DIR="/home/brian11hwang/SR-IOV/iperf_test/new_test/test3"

# Outer loop for 10 times execution
for (( j=1; j<=10; j++ ))
do
  # Loop from 1 to 9
  for (( i=1; i<=9; i++ ))
  do
    echo "Running iperf with P value $i"
    
    # Run iperf and capture the output
    output=$(nice -n 10 iperf -c $IP -t $TIME -w $WINDOW_SIZE -P $i)
    
    # Extract the bandwidth value, assuming it's the last field in the output
    bandwidth=$(echo "$output" | tail -n 3 | awk '{print $(NF-1)}' | tail -n 1)
    
    # Convert bandwidth (assumed to be in Mbits/sec) to a number
    bandwidth_num=$(echo $bandwidth | sed 's/[A-Za-z]*//g')

    # Output file
    OUTPUT_FILE="${BASE_DIR}/bandwidth_P${i}_iteration${j}.txt"

    # Write bandwidth to file
    echo "Bandwidth for P=$i, iteration $j: $bandwidth_num Mbits/sec" > $OUTPUT_FILE
  done
done

