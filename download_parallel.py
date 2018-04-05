import time
import threading
import Queue
import urllib2

# utility - spawn a thread to execute target for each args
def run_parallel_in_threads(target, args_list):
    result = Queue.Queue()
    # wrapper to collect return value in a Queue
    def task_wrapper(*args):
        result.put(target(*args))
    threads = [threading.Thread(target=task_wrapper, args=args) for args in args_list]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return result

# below is the application code
urls = [
    ('https://en.wikipedia.org/wiki/Apple',),
    ('https://en.wikipedia.org/wiki/Pear',),
    ('https://en.wikipedia.org/wiki/Banana',),
    ('https://en.wikipedia.org/wiki/Carrot',),
    ('https://en.wikipedia.org/wiki/Watermelon',),
]

def fetch(url):
    return urllib2.urlopen(url).read()

q = run_parallel_in_threads(fetch, urls)
print q.qsize()
q.get()
print q.qsize()
q.get()
print q.qsize()