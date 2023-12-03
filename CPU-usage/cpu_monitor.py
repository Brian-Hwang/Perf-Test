import psutil
import time
import argparse
import csv
import os

def find_processes_by_prefix(prefix):
    """Find all processes whose name starts with the given prefix."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        if prefix in proc.info['name']:
            processes.append(proc)
    print(f"Found {len(processes)} processes with the prefix '{prefix}'.")
    return processes

def get_process_info(proc):
    """Get process information including PID, name, and CPU cores used."""
    try:
        return {
            'pid': proc.pid,
            'name': proc.name(),
            'cpu_cores': proc.cpu_affinity()
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return None

def monitor_cpu_usage(processes, duration, interval):
    """Monitor the CPU usage of the given processes over the specified duration."""
    end_time = time.time() + duration
    cpu_usage = {proc.pid: [] for proc in processes}  # Initialize with all processes

    while time.time() < end_time:
        for proc in processes:
            try:
                usage = proc.cpu_percent(interval=None)  # Non-blocking call
                cpu_usage[proc.pid].append(usage)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass  # Process might have ended or access denied
        time.sleep(interval)  # Wait for the interval
    time.sleep(5)  # Final wait for 5 seconds

    return cpu_usage

def write_results_to_csv(file_path, all_cpu_usage_data):
    """Write the CPU monitoring results to a CSV file."""
    with open(file_path, mode='w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(['Number of Jobs (Per NVMe)', 'Target Used CPU Cores', 'Target CPU Usage'])

        for iteration, cpu_usage_data in enumerate(all_cpu_usage_data, 1):
            row = [iteration]
            cores = []
            usages = []
            for pid, usages_list in cpu_usage_data.items():
                if usages_list:
                    avg_usage = sum(usages_list) / len(usages_list)
                    if avg_usage > 0:
                        proc_info = get_process_info(psutil.Process(pid))
                        if proc_info:
                            cores.append(str(proc_info['cpu_cores']))
                            usages.append(f"{avg_usage:.2f}%")
            row.append(', '.join(cores))
            row.append(', '.join(usages))
            csv_writer.writerow(row)

def main():
    parser = argparse.ArgumentParser(description='Monitor CPU usage of processes with a specific command prefix.')
    parser.add_argument('--prefix', default='nvmet_tcp_wq', help='Command prefix to monitor (default: "nvmet_tcp_wq")')
    parser.add_argument('--duration', '-d', type=int, default=30, help='Duration to monitor in seconds (default: 30)')
    parser.add_argument('--interval', '-n', type=int, default=5, help='Interval to check CPU usage in seconds (default: 5)')
    parser.add_argument('--iterations', '-i', type=int, default=1, help='Number of iterations to perform (default: 1)')
    parser.add_argument('--output', '-o', default='/home/brian11hwang/NVMe/cpu_usage_results.csv', help='Output file path (default: /home/brian11hwang/NVMe/cpu_usage_results.csv)')
    args = parser.parse_args()

    all_cpu_usage_data = []
    for iteration in range(args.iterations):
        time.sleep(5)
        processes = find_processes_by_prefix(args.prefix)
        if not processes:
            print(f"No processes found with the prefix: {args.prefix}")
            continue

        cpu_usage_data = monitor_cpu_usage(processes, args.duration, args.interval)
        all_cpu_usage_data.append(cpu_usage_data)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    write_results_to_csv(args.output, all_cpu_usage_data)
    print(f"Results written to {args.output}")

if __name__ == "__main__":
    main()
