__author__ = 'vladimir'
from xml.sax.handler import ContentHandler
import threading
import concurrent.futures
import queue
from queue import Empty
from time import sleep
import multiprocessing as mp


WORKER_NUM = 8


class ContentRetriever(ContentHandler):
    def __init__(self, page_handler):
        self.handler = page_handler
        self.docs = mp.Queue(40)
        self.doc_id = ""
        self.doc_url = ""
        self.encoded_content = ""
        self.current_tag = ""
        self.lock = mp.Lock()
        self.workers = [mp.Process(target=self.handleDocs, args=(self.docs, self.lock, i,)) for i in range(WORKER_NUM)]
        # self.errors = queue.Queue(100)
        for w in self.workers:
            w.start()
        # for _ in range(WORKER_NUM):
        #     self.workers.submit(self.handleDocs, self.docs)


        # self.errorlog = open("errors", "w")

    def characters(self, content):
        if self.current_tag == "docID":
            self.doc_id += content
        elif self.current_tag == "docURL":
            self.doc_url += content
        elif self.current_tag == "content":
            self.encoded_content += content

    def endDocument(self):
        for _ in range(WORKER_NUM * 2):
            self.docs.put(None)
        for w in self.workers:
            w.join(1)
        self.handler.stats.summarize()
        print("Finished document")

    def startElement(self, name, attrs):
        if name == "document":
            self.doc_id = ""
            self.doc_url = ""
            self.encoded_content = ""
        self.current_tag = name

    # the main producer
    def endElement(self, name):
        if name == "document":
            # while not self.errors.empty():
            #     print(self.errors.get())
            # try:
            #     self.handler.handlePage(self.doc_id, self.doc_url, self.encoded_content)
            # except:
            #     pass
            self.docs.put((self.doc_id, self.doc_url, self.encoded_content))
            # print("Put element into the queue!")
            if int(self.doc_id) % 10000 == 0:
                print(self.doc_id)
                # print(str(self.handler.stats))
                # self.handler.stats.summarize()
            # self.handleDocs(self.docs)

    # consumer
    def handleDocs(self, q, lock, i):
        while True:
            # otherwise causes exit code 135
            try:
                data = q.get()
                # print("Fetched in", i, "thanks!")
                if data is None:
                    break
                doc_id, doc_url, content = data
                self.handler.handlePage(doc_id, doc_url, content, lock)
            except Empty:
                # print("Waiting in", i)
                sleep(0.01)

    def startDocument(self):
        print("Started analysing")
