import subprocess
import csv
from tqdm import tqdm

# Define the different configurations
memory_sizes = ['1G', '10G', '100G']
memory_operations = ['read', 'write']
thread_counts = [1, 8, 16, 32]

# Function to convert MiB/sec to Gbps
def convert_to_gbps(mib_sec):
    return (mib_sec * 8) / 953.674

# Function to run sysbench and parse output
def run_sysbench(mem_size, mem_oper, threads):
    command = f"sudo sysbench memory --memory-block-size=1K --memory-scope=global --memory-total-size={mem_size} --memory-oper={mem_oper} --threads={threads} run"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = result.stdout
    print(command)
    # Parse the output for MiB/sec value
    for line in output.split('\n'):
        if "MiB/sec" in line:
            mib_sec = float(line.split()[3][1:])
            print(mib_sec)
            return mib_sec, convert_to_gbps(mib_sec)
    return None, None

# CSV file setup
csv_file = 'sysbench_results.csv'
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Memory Size', 'Operation', 'Threads', 'Speed (MiB/sec)', 'Speed (Gbps)'])

    # Total number of iterations for the progress bar
    total_iterations = len(memory_sizes) * len(memory_operations) * len(thread_counts)

    with tqdm(total=total_iterations, desc="Running sysbench tests") as pbar:
        # Run sysbench for each configuration and write results to CSV
        for size in memory_sizes:
            for operation in memory_operations:
                for threads in thread_counts:
                    mib_sec, speed_gbps = run_sysbench(size, operation, threads)
                    writer.writerow([size, operation, threads, mib_sec, speed_gbps])
                    pbar.update(1)  # Update progress bar after each iteration

print(f"Results saved to {csv_file}")
