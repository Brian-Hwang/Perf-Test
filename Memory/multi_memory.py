import psutil
import time
import csv

def get_memory_usage():
    """
    Returns the current memory usage.
    """
    memory = psutil.virtual_memory()
    return memory.used  # returns used memory in bytes

def average_memory_usage(interval, duration):
    """
    Calculates the average memory usage over a given duration and interval.
    """
    usage_data = []
    time_elapsed = 0

    while time_elapsed < duration:
        usage_data.append(get_memory_usage())
        time.sleep(interval)
        time_elapsed += interval

    return sum(usage_data) / len(usage_data)

def write_to_csv(file_name, data):
    """
    Writes data to a CSV file.
    """
    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Measurement Number', 'Average Memory Usage (Bytes)'])
        for i, memory_usage in enumerate(data, 1):
            writer.writerow([i, memory_usage])

def main():
    measurements = []
    interval = 1  # seconds
    duration = 30  # seconds
    total_measurements = 7  # number of times to measure
    total_cycle_time = 40  # Total time for each cycle in seconds

    for _ in range(total_measurements):
        start_time = time.time()  # Start timing the cycle

        avg_memory_usage = average_memory_usage(interval, duration)
        print(avg_memory_usage)
        measurements.append(avg_memory_usage)

        elapsed_time = time.time() - start_time  # Calculate elapsed time
        sleep_time = max(0, total_cycle_time - elapsed_time - duration)  # Calculate remaining time for 40-second cycle
        time.sleep(sleep_time)  # Sleep for the remaining time

    write_to_csv('memory_usage.csv', measurements)

if __name__ == "__main__":
    main()
