import subprocess
import psutil
import time
import re
import csv
import os
import time

def get_memory_usage():
    memory = psutil.virtual_memory()
    return memory.used

def average_memory_usage(interval, duration):
    usage_data = []
    time_elapsed = 0

    while time_elapsed < duration:
        usage_data.append(get_memory_usage())
        time.sleep(interval)
        time_elapsed += interval

    return sum(usage_data) / len(usage_data)

def create_fio_config(num_jobs, filename="/dev/nvme4n1"):
    config = [
        "[global]",
        "rw=randread",
        "bs=64k",
        "iodepth=32",
        "direct=1",
        "ioengine=libaio",
        "group_reporting",
        "time_based",
        "runtime=30",
        "size=1G",
        "norandommap",
        "prioclass=1",
        "gtod_reduce=0",
    ]
    num_jobs=4
    for job in range(1, num_jobs + 1):
        config.extend([
            f"[job{job}]",
            f"cpus_allowed={29 + job}",
            f"filename={filename}",
            "numjobs=1"
        ])

    return '\n'.join(config)

def parse_fio_output(output, num_jobs):
    # print(output)
    results = []
    for line in output.split('\n'):
        if 'read: IOPS=' in line:
            iops_match = re.search(r'IOPS=(\d+\.?\d*)k', line)
            bw_match = re.search(r'BW=(\d+)MiB/s', line)

            if iops_match and bw_match:
                iops = float(iops_match.group(1)) * 1000  # Convert kIOPS to IOPS
                bw_mib = int(bw_match.group(1))
                bw_gbps = bw_mib * 8 / 1024  # Convert MiB/s to Gbps
                results.append((num_jobs, iops, bw_mib, bw_gbps))

    return results

def save_to_csv(data, file_name, mode='w'):
    dir_name = os.path.dirname(file_name)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(file_name, mode, newline='') as file:
        writer = csv.writer(file)
        if mode == 'w':
            writer.writerow(['Number of Jobs', 'IOPS', 'BW (MiB/s)', 'BW (Gbps)', 'Average Memory Usage (MB)'])
        for record in data:
            writer.writerow(record)

def main():
    base_dir = '/home/brian11hwang/NVMe/Perf-Test/NVMe/'
    csv_file = f"{base_dir}fio_results.csv"
    interval = 1
    total_measurements = 10
    duration = 30
    total_cycle_time = 40  # Total time for each cycle

    all_results = []

    # Baseline memory usage measurement without running fio
    start_time = time.time()
    baseline_average_usage = average_memory_usage(interval, duration) / (1024**2)  # Convert to MB
    all_results.append(('No Job', 0, 0, 0, baseline_average_usage))
    elapsed_time = time.time() - start_time
    sleep_time = max(0, total_cycle_time - elapsed_time)
    time.sleep(sleep_time)

    for num_jobs in range(1, total_measurements):  # Run for 1, 2 jobs
        start_time = time.time()

        conf_file = f"{base_dir}temp_conf_{num_jobs}.conf"
        with open(conf_file, 'w') as file:
            file.write(create_fio_config(num_jobs))

        # Run fio command and capture the output
        result = subprocess.run(f"fio {conf_file}", shell=True, capture_output=True, text=True)
        output = result.stdout

        # Parse and collect the results
        parsed_results = parse_fio_output(output, num_jobs)

        # Calculate the average memory usage
        average_usage = average_memory_usage(interval, duration) / (1024**2)  # Convert to MB

        for parsed_result in parsed_results:
            all_results.append((num_jobs,) + parsed_result + (average_usage,))

        # for iops, bw_mib, bw_gbps in parsed_results:
        #     all_results.append((num_jobs, iops, bw_mib, bw_gbps, average_usage))

        # Remove the temporary configuration file
        os.remove(conf_file)

        # Calculate remaining time and sleep accordingly
        elapsed_time = time.time() - start_time
        sleep_time = max(0, total_cycle_time - elapsed_time)
        time.sleep(sleep_time)

    # Save all results to CSV
    save_to_csv(all_results, csv_file)

if __name__ == "__main__":
    main()

