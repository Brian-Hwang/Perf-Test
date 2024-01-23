# BEFORE RUNNING THE SCRIPT: 
# sudo pip3 install tqdm && sudo pip3 install psutil
# pip3 install tqdm && sudo pip3 install psutil


# Use Example: 
# python3 multi_ContentionAndUsage.py -o 20 -s 5 -t 10 -c "50-53" -v 4 -b 25600 -m 20


import argparse
import subprocess
import time
import psutil
import csv
import threading
from tqdm import tqdm

def run_stress_command(duration, taskset_cores, vm_number, vm_bytes):
    """
    Runs the stress command with specified parameters and prints the output.
    """
    cmd = f"taskset -c {taskset_cores} stress --vm {vm_number} --vm-bytes {vm_bytes}M --timeout {duration}s"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    # Print any error if occurred
    if result.stderr:
        print("Error:")
        print(result.stderr)

def get_memory_usage():
    """
    Returns the current memory usage in bytes.
    """
    memory = psutil.virtual_memory()
    return memory.used

def average_memory_usage(interval, duration, usage_data):
    """
    Calculates the average memory usage over a given duration and interval.
    """
    time_elapsed = 0
    while time_elapsed < duration:
        usage_data.append(get_memory_usage())
        time.sleep(interval)
        time_elapsed += interval

def write_to_csv(file_name, data):
    """
    Writes data to a CSV file, converting memory usage to GB.
    """
    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Iteration', 'Average Memory Usage (GB)'])
        for label, memory_usage in data:
            memory_usage_gb = memory_usage / (1024 ** 3)
            writer.writerow([label, memory_usage_gb])

def parse_arguments():
    """
    Parses command line arguments.
    """
    parser = argparse.ArgumentParser(description='Script to perform memory stress testing and monitor memory usage.')
    parser.add_argument('-o', '--operation_duration', type=int, default=20, help='Duration for each memory and stress test operation (in seconds). Default: 20')
    parser.add_argument('-s', '--sleep_duration', type=int, default=5, help='Sleep duration between operations (in seconds). Default: 5')
    parser.add_argument('-t', '--total_iterations', type=int, default=10, help='Total number of iterations. Default: 10')
    parser.add_argument('-c', '--taskset_cores', default='50-53', help='CPU cores to use for the stress test (e.g., "50-53"). Default: "50-53"')
    parser.add_argument('-v', '--vm_number', type=int, default=4, help='Number of VM workers for stress test. Default: 4')
    parser.add_argument('-b', '--vm_bytes', type=int, default=256*100, help='Memory for each VM worker (in MB). Default: 25600')
    parser.add_argument('-m', '--memory_measurement_duration', type=int, default=20, help='Memory measurement duration (in seconds). Default: 20')
    return parser.parse_args()

def main():
    args = parse_arguments()

    memory_measurements = []

    with tqdm(total=args.total_iterations + 1, desc="Baseline", unit="iteration") as pbar:
        # Baseline measurement without stress
        usage_data = []
        average_memory_usage(1, args.memory_measurement_duration, usage_data)
        avg_memory_usage = sum(usage_data) / len(usage_data)
        memory_measurements.append(("Baseline", avg_memory_usage))
        pbar.update(1)  # Update progress bar after baseline

        # Stress test iterations
        for iteration in range(1, args.total_iterations + 1):
            pbar.set_description(f"Iteration {iteration}")  # Update description for each iteration
            usage_data = []

            stress_thread = threading.Thread(target=run_stress_command, args=(args.operation_duration, args.taskset_cores, args.vm_number, args.vm_bytes))
            stress_thread.start()

            average_memory_usage(1, args.memory_measurement_duration, usage_data)

            stress_thread.join()

            avg_memory_usage = sum(usage_data) / len(usage_data)
            memory_measurements.append((iteration, avg_memory_usage))

            time.sleep(args.sleep_duration)

            pbar.update(1)  # Update progress bar after each iteration

    write_to_csv('memory_usage.csv', memory_measurements)

if __name__ == "__main__":
    main()



#Use Example: python3 multi_ContentionAndUsage.py -o 20 -s 5 -t 10 -c "50-53" -v 4 -b 25600 -m 20