import time
import numpy as np

def consume_memory(memory_per_sec_mb, duration_sec):
    memory_blocks = []

    for _ in range(duration_sec):
        start_time = time.time()

        # Allocate memory_per_sec_mb of memory
        memory_blocks.append(np.ones((memory_per_sec_mb, 1024, 1024), dtype=np.uint8))
        
        # Calculate the time taken for the allocation
        allocation_time = time.time() - start_time

        # Sleep for the remaining time of the second, if any
        sleep_duration = max(0, 1 - allocation_time)
        time.sleep(sleep_duration)

# Example usage: Consume 5MB per second for 60 seconds
consume_memory(100, 30)
