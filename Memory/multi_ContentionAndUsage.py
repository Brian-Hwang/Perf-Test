# BEFORE RUNNING THE SCRIPT: 
# sudo apt install stress && sudo apt install mbw
# sudo pip3 install tqdm && sudo pip3 install psutil
# pip3 install tqdm && sudo pip3 install psutil

# Use Example:
#With NUMA:
#python3 multi_ContentionAndUsage.py -d 30 -s 10 -t 5 -c "0-3" -v 2 -b 25600 -m 1024 -n 1
#Without NUMA:
# python3 multi_ContentionAndUsage.py -d 30 -s 10 -t 5 -c "0-3" -v 2 -b 25600 -m 1024

# Caution!
# The given taskset core for the python script will not match the core given for the "Stress" memory benchmark
# Thus, designate wanted NUMA CPU Number and Cores with the options provided

import argparse
import subprocess
import time
import psutil
import csv
import threading
from tqdm import tqdm

def calculate_vm_number_and_cores(taskset_cores):
    cores = list(map(int, taskset_cores.split('-')))
    vm_number = max(1, cores[-1] - cores[0])  # At least 1 VM
    stress_cores = '-'.join(map(str, [cores[0], cores[-1] - 1]))  # First to second-last core
    mbw_core = str(cores[-1])  # Last core
    return vm_number, stress_cores, mbw_core


def run_stress_command(duration, taskset_cores, vm_bytes, numa):
    """
    Runs the stress command with specified parameters using numactl if numa is set, otherwise uses taskset.
    Suppresses the output by redirecting it to /dev/null.
    """
    vm_number, stress_cores, _ = calculate_vm_number_and_cores(taskset_cores)
    with open('/dev/null', 'w') as devnull:
        if numa != -1:
            cmd = f"numactl -C {stress_cores} -N {numa} -m {numa} taskset -c {stress_cores} stress --vm {vm_number} --vm-bytes {vm_bytes}M --timeout {duration}s"
        else:
            cmd = f"taskset -c {stress_cores} stress --vm {vm_number} --vm-bytes {vm_bytes}M --timeout {duration}s"
        
        subprocess.run(cmd, shell=True, stdout=devnull, stderr=devnull)


def run_mbw(mem_size, taskset_cores, numa):
    """
    Runs the mbw command to measure memory bandwidth and returns the average copy bandwidth.
    """
    _, _, mbw_core = calculate_vm_number_and_cores(taskset_cores)
    if numa != -1:
        cmd = f"numactl -C {mbw_core} -N {numa} -m {numa} taskset -c {mbw_core} mbw -t0 {mem_size}"
    else:
        cmd = f"taskset -c {mbw_core} mbw -t0 {mem_size}"

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stderr:
        print("Error running mbw:")
        print(result.stderr)
    return parse_mbw_output(result.stdout)

def parse_mbw_output(mbw_output):
    """
    Parses the output from mbw to extract the average copy bandwidth.
    """
    avg_bw = "N/A"
    for line in mbw_output.split('\n'):
        if line.startswith("AVG"):
            parts = line.split()
            if len(parts) >= 5:
                
                avg_bw = parts[-2]  # The average bandwidth is in the fifth position
                break
    return avg_bw



def get_memory_usage():
    """
    Returns the current memory usage in bytes.
    """
    memory = psutil.virtual_memory()
    return memory.used

def average_memory_usage(interval, duration, usage_data):
    """
    Calculates the average memory usage over a given duration and interval.
    Adjusts sleep intervals for more accurate timing.
    """
    start_time = time.time()
    while (time.time() - start_time) < duration:
        measure_start = time.time()
        
        usage_data.append(get_memory_usage())
        
        measure_end = time.time()
        measure_duration = measure_end - measure_start
        time_to_sleep = max(0, interval - measure_duration)
        
        time.sleep(time_to_sleep)

def write_to_csv(file_name, memory_data, mbw_data):
    """
    Writes data to a CSV file, converting memory usage to GB and including mbw results.
    """
    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Iteration', 'Average Memory Usage (GB)', 'Memory Copy Throughput(MiB/s)'])
        for i, (label, memory_usage) in enumerate(memory_data):
            memory_usage_gb = memory_usage / (1024 ** 3)
            mbw_output = mbw_data[i]
            writer.writerow([label, memory_usage_gb, mbw_output])

def parse_arguments():
    """
    Parses command line arguments.
    """
    parser = argparse.ArgumentParser(description='Script to perform memory stress testing and monitor memory usage.')
    parser.add_argument('-d', '--operation_duration', type=int, default=20, help='Duration for each memory and stress test operation (in seconds). Default: 20')
    parser.add_argument('-s', '--sleep_duration', type=int, default=5, help='Sleep duration between operations (in seconds). Default: 5')
    parser.add_argument('-t', '--total_iterations', type=int, default=10, help='Total number of iterations. Default: 10')
    parser.add_argument('-c', '--taskset_cores', default='50-53', help='CPU cores to use for the stress test (e.g., "50-53"). Default: "50-53"')
    parser.add_argument('-b', '--vm_bytes', type=int, default=256*100, help='Memory for each VM worker (in MB). Default: 25600')
    parser.add_argument('-n', '--numa', type=int, default=-1, help='NUMA node and memory number. Set to -1 to disable. Default: -1')
    parser.add_argument('-m', '--mbw_mem_size', type=int, default=1024, help='Memory size for mbw test in MB. Default: 1024')

    return parser.parse_args()

def main():
    args = parse_arguments()

    memory_measurements = []
    mbw_measurements = []

    with tqdm(total=args.total_iterations + 1, desc="Baseline", unit="iteration") as pbar:
        # Baseline measurement without stress
        usage_data = []
        average_memory_usage(1, 1, usage_data)
        avg_memory_usage = sum(usage_data) / len(usage_data)
        memory_measurements.append(("Baseline", avg_memory_usage))
        
        # Wait half the operation duration before running mbw
        time.sleep(args.operation_duration / 2)
        mbw_output = run_mbw(args.mbw_mem_size, args.taskset_cores, args.numa)
        mbw_measurements.append(mbw_output)
        pbar.update(1)

        # Stress test iterations
        for iteration in range(1, args.total_iterations + 1):
            pbar.set_description(f"Iteration {iteration}")
            usage_data = []

            stress_thread = threading.Thread(target=run_stress_command, args=(args.operation_duration, args.taskset_cores, args.vm_bytes, args.numa))
            stress_thread.start()

            # Wait half the operation duration before running mbw
            time.sleep(args.operation_duration / 2)
            mbw_output = run_mbw(args.mbw_mem_size, args.taskset_cores, args.numa)
            mbw_measurements.append(mbw_output)

            # Complete the remaining stress test duration
            remaining_duration = args.operation_duration - (args.operation_duration / 2)
            average_memory_usage(1, remaining_duration, usage_data)

            stress_thread.join()

            avg_memory_usage = sum(usage_data) / len(usage_data)
            memory_measurements.append((iteration, avg_memory_usage))

            time.sleep(args.sleep_duration)

            pbar.update(1)

    write_to_csv('memory_usage.csv', memory_measurements, mbw_measurements)

if __name__ == "__main__":
    main()
