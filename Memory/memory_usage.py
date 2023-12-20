import psutil
import time

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

# Set your desired interval (in seconds) and duration (in seconds)
interval = 1
duration = 30

# Calculate and print the average memory usage
average_usage = average_memory_usage(interval, duration)
print(f"Average Memory Usage: {average_usage / (1024**2):.2f} MB")
