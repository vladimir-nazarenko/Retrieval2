import concurrent.futures as cf
import threading
import queue

NUM_CPUS = 5
NUM_THREADS = 10
MAX_QUEUE_SIZE = 200

# Runs in worker processes.
def producer(i):
    return i + 10

def consumer(i):
    global total
    # We need to protect this with a lock because
    # multiple threads in the main program can
    # execute this function simultaneously.
    with sumlock:
        total += i

# Runs in threads in main program.
def consume_results(q):
    while True:
        future = q.get()
        if future is None:
            break
        else:
            consumer(future.result())

if __name__ == "__main__":
    sumlock = threading.Lock()
    result_queue = queue.Queue(MAX_QUEUE_SIZE)
    total = 0
    NUM_TO_DO = 100000
    with cf.ThreadPoolExecutor(NUM_THREADS) as tp:
        # start the threads running `consume_results`
        for _ in range(NUM_THREADS):
            tp.submit(consume_results, result_queue)
        # start the worker processes
        with cf.ProcessPoolExecutor(NUM_CPUS) as pp:
            for i in range(NUM_TO_DO):
                # blocks until the queue size <= MAX_QUEUE_SIZE
                result_queue.put(pp.submit(producer, i))
        # tell threads we're done
        for _ in range(NUM_THREADS):
            result_queue.put(None)
    print("got", total, "expected", (10 + NUM_TO_DO + 9) * NUM_TO_DO // 2)
