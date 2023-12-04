import subprocess
import argparse
import re
import csv
import os
import json

def generate_fio_config(num_jobs, file_path_options, converged, bs, iodepth):
    base_config = f'''[global]
bs={bs}
iodepth={iodepth}
direct=1
ioengine=libaio
group_reporting
time_based
runtime=30
filesize=1G
norandommap
prioclass=0
gtod_reduce=0
group_reporting
'''

    job_configs = []
    job_count = 0
    for i in range(num_jobs):
        for file_path_option in file_path_options:
            job_config = f'''[job{job_count+1}]
rw=randread
filename=/mnt/{file_path_option}/1g_file_{i}'''
            job_config += f'\ncpus_allowed={job_count+5}'
            job_configs.append(job_config)
            job_count += 1

    full_config = base_config + '\n\n'.join(job_configs)
    return full_config

def run_fio(num_jobs, file_path_options, converged, bs, iodepth):
    config = generate_fio_config(num_jobs, file_path_options, converged, bs, iodepth)
    with open("temp_job.conf", "w") as file:
        file.write(config)

    result = subprocess.run(["fio", "temp_job.conf"], capture_output=True, text=True)
    return result.stdout

def parse_fio_output(output, num_jobs):
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
            writer.writerow(['Number of Jobs', 'IOPS', 'BW (MiB/s)', 'BW (Gbps)'])
        for num_jobs, iops, bw_mib, bw_gbps in data:
            writer.writerow([num_jobs, iops, bw_mib, bw_gbps])

def get_csv_filename_for_converged(file_paths):
    if 'all' in file_paths:
        return 'results/fio_results_converged_all.csv'
    else:
        file_path_str = '_'.join(file_paths)
        return f'results/fio_results_converged_{file_path_str}.csv'

def load_config(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def main():
    config = load_config('config.json')
    all_file_paths = config['all_file_paths']

    parser = argparse.ArgumentParser(description='Run fio benchmark.')
    parser.add_argument('-i', '--jobs', type=int, required=True, help='Number of jobs')
    parser.add_argument('-fp', '--filepath', nargs='+', required=True, help='File path option(s)')
    parser.add_argument('-c', '--converged', action='store_true', help='Run converged file paths')
    parser.add_argument('-bs', '--blocksize', type=str, default='128k', help='Block size')
    parser.add_argument('-io', '--iodepth', type=int, default=32, help='I/O depth')

    args = parser.parse_args()

    file_paths = all_file_paths if 'all' in args.filepath else args.filepath

    if args.converged:
        csv_file_name = get_csv_filename_for_converged(file_paths)
        for nj in range(1, args.jobs + 1):
            print(f"Running {nj} job(s) for file paths: {file_paths} in converged mode")
            output = run_fio(nj, file_paths, True, args.blocksize, args.iodepth)
            results = parse_fio_output(output, nj)
            save_to_csv(results, csv_file_name, mode='a' if nj > 1 else 'w')
            print(f"Results saved to {csv_file_name}")
    else:
        for file_path_option in file_paths:
            print(f"Running benchmark for file path: {file_path_option}")
            results = []
            for nj in range(1, args.jobs + 1):
                print(f"Running {nj} job(s) for file path: {file_path_option}")
                output = run_fio(nj, [file_path_option], False, args.blocksize, args.iodepth)
                results.extend(parse_fio_output(output, nj))

            csv_file_name = f'results/fio_results_{file_path_option}.csv'
            save_to_csv(results, csv_file_name)
            print(f"Results saved to {csv_file_name}")

if __name__ == "__main__":
    main()
