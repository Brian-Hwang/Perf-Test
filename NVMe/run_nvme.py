import argparse
import os

def build_command(args):
    # Set defaults
    runtime = args.runtime if args.runtime else "30"
    core_num = args.core_num if args.core_num else "5"
    bs = str(int(args.block_size)) + "k" if args.block_size and args.block_size.isdigit() else args.block_size if args.block_size else "4k"
    io_type = args.io_type if args.io_type else "randread"
    io_depth = args.io_depth if args.io_depth else "1"
    file_id = args.file_id if args.file_id else "0"
    prio_class = args.prio_class if args.prio_class else "0"

    # Mapping file_path argument to specific paths
    file_path_mappings = {
        "1": "/mnt/first",
        "2": "/mnt/second",
        "3": "/mnt/third"
    }
    file_path = file_path_mappings.get(args.file_path, "/mnt/first")

    file_name = f"{file_path}/1g_file_{file_id}"

    # Adjusting command based on core_num
    core_cmd = "" if core_num.lower() == "no" else f"taskset -c {core_num} "
    
    cmd = f"sudo {core_cmd}fio --name=nvme-test --ioengine=libaio --time_based " \
          f"--runtime={runtime} --iodepth={io_depth} --rw={io_type} --norandommap " \
          f"--thread=1 --prioclass={prio_class} --cpus_allowed_policy=split --bs={bs} " \
          f"--direct=1 --numjobs=1 --filename={file_name} --group_reporting --gtod_reduce=0"
    
    return cmd

def main():
    parser = argparse.ArgumentParser(description='Run block switch test with fio.')
    parser.add_argument('-b', '--block-size', help='Block size in KB without the "k" (e.g., 4 for 4k)')
    parser.add_argument('-t', '--io-type', help='IO type (e.g., randread, randwrite)')
    parser.add_argument('-d', '--io-depth', help='IO depth')
    parser.add_argument('-c', '--core-num', help='Core number (use "no" to skip taskset)')
    parser.add_argument('-p', '--prio-class', help='Priority class')
    parser.add_argument('-f', '--file-id', help='File ID')
    parser.add_argument('-r', '--runtime', help='Runtime in seconds')
    parser.add_argument('-fp', '--file-path', help='File path option (1, 2, or 3)', choices=['1', '2', '3'])
    
    args = parser.parse_args()

    cmd = build_command(args)
    print(cmd)
    os.system(cmd)

if __name__ == "__main__":
    main()
