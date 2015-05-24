__author__ = 'vladimir'
from re import findall
from pymorphy2 import MorphAnalyzer
from collections import defaultdict
from math import log2
from multiprocessing import Manager, Process, Pool, Queue, Lock
from queue import Empty
from time import sleep, time, localtime

WORKER_COUNT = 5


class Manager:
    def __init__(self):
        self.stopwords = set()
        with open("stopwords.txt", "r") as f:
            for line in f:
                self.stopwords.add(line.strip("\n "))
            self.stops_num = len(self.stopwords)
        self.tasks = Queue(20)
        self.consumers = [Process(target=parse, args=(MorphAnalyzer(), self.tasks, self.stopwords, self.stops_num))
                          for _ in range(WORKER_COUNT)]
        self.producer = Process(target=self.produce, args=())
        # self.analyzers = Queue(WORKER_COUNT)
        # for i in range(WORKER_COUNT):
        #     self.analyzers.put(MorphAnalyzer())

    def produce(self):
        with open("collection_task6.tsv", "r") as f:
            cnt = 0
            for line in f:
                cnt += 1
                if cnt % 10000 == 0:
                    print("produced" + str(cnt))
                self.tasks.put(line)

    def start(self):
        self.producer.start()
        for w in self.consumers:
            w.start()

    def join(self):
        self.producer.join()
        for _ in range(WORKER_COUNT * 2):
            self.tasks.put(None)
        for w in self.consumers:
            w.join()


# consumer thread independent
def parse(morph, queue, stopwords, stops_num):
    while True:
        try:
            line = queue.get()
            # log_info("Fetched item")
            if line is None:
                break
        except Empty:
            sleep(0.01)
        features = line.split("\t")
        txt = features[3]
        # word_count = int(features[4])
        # list_of_words = [morph.parse(w)[0].normal_form for w in findall("[a-zA-Z0-9а-яА-Я]+", txt)]
        list_of_words = findall("[a-zA-Z0-9а-яА-Я]+", txt)
        word_count = len(list_of_words)
        # print(list_of_words)
        sw = set()
        num_of_stops = 0
        freqs = defaultdict(int)
        for w in list_of_words:
            freqs[w] += 1
            # calculate entropy
            entropy = 0
        try:
            for w in freqs.keys():
                probabil = freqs[w] / word_count
                entropy -= probabil * log2(probabil)
        except ZeroDivisionError:
            entropy = 0
        # deal with stopwords
        for word in list_of_words:
            if word in stopwords:
                sw.add(word)
                num_of_stops += 1
        try:
            frac_stops = len(sw) / stops_num
        except ZeroDivisionError:
            frac_stops = 0
        try:
            stops_percentage = num_of_stops / len(list_of_words)
        except ZeroDivisionError:
            stops_percentage = 0
        result_list = [features[0], str(frac_stops), str(stops_percentage), str(entropy)]
        log_info(" ".join(result_list) + "\n")


# consumer thread dependant
def log_info(info):
    with lock:
        out.write(info)

if __name__ == '__main__':
    start = time()
    print("Started at {0}".format(localtime(start)))
    out = open("quality_features.txt", "w")
    lock = Lock()
    m = Manager()
    m.start()
    m.join()
    out.close()
    print("Elapsed {0} seconds".format(time() - start))