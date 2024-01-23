import subprocess
import time

def run_stress_command(execution_number):
    """
    Runs the stress command with specified parameters and varying --vm-bytes based on the execution number.
    """
    # vm_bytes = 256 * execution_number  # Multiply 256M by the execution number
    vm_bytes = 256 * 100
    cmd = f"taskset -c 50-53 stress --vm 4 --vm-bytes {vm_bytes}M --timeout 30s"
    subprocess.run(cmd, shell=True)

def main():
    total_cycle_time = 40  # Total time for each cycle in seconds
    total_measurements = 10  # number of times to run the command
    
    #for baseline
    time.sleep(total_cycle_time)
    
    for execution_number in range(1, total_measurements + 1):
        start_time = time.time()

        # Run the stress command with increasing --vm-bytes
        run_stress_command(execution_number)

        # Calculate remaining time and sleep accordingly
        elapsed_time = time.time() - start_time
        sleep_time = max(0, total_cycle_time - elapsed_time)
        time.sleep(sleep_time)

if __name__ == "__main__":
    main()
