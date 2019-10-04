import time


def time_counter(gap):
    time_start = time.time()
    time_now = time.time()
    while time_now - time_start < gap:
        time_now = time.time()
