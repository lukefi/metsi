import time

start_time = time.time_ns()


def runtime_now() -> float:
    global start_time
    return round((time.time_ns() - start_time) / 1000000000, 1)


def print_logline(message: str):
    print("{} {}".format(runtime_now(), message))
