__author__ = 'vladimir'
from xml.sax.handler import ContentHandler
import threading
import concurrent.futures
import queue
from time import sleep
import multiprocessing as mp


WORKER_NUM = 7


class ContentRetriever(ContentHandler):
    def __init__(self, page_handler):
        self.handler = page_handler
        self.docs = queue.Queue(500)
        self.doc_id = ""
        self.doc_url = ""
        self.encoded_content = ""
        self.current_tag = ""
        self.workers = concurrent.futures.ThreadPoolExecutor(WORKER_NUM)
        # for _ in range(WORKER_NUM):
        #     self.workers.submit(self.handleDocs, self.docs)
        # self.lock = mp.Lock()
        # self.errorlog = open("errors", "w")


    def characters(self, content):
        if self.current_tag == "docID":
            self.doc_id += content
        elif self.current_tag == "docURL":
            self.doc_url += content
        elif self.current_tag == "content":
            self.encoded_content += content

    def endDocument(self):
        for _ in range(WORKER_NUM):
            self.docs.put(None)
        self.workers.shutdown(True)
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
            self.handler.handlePage(self.doc_id, self.doc_url, self.encoded_content)
            # self.docs.put((self.doc_id, self.doc_url, self.encoded_content))
            if int(self.doc_id) % 1000 == 0:
                print(self.doc_id)
            # self.handleDocs(self.docs)

    # def handleDocs(self, q):
    #     while True:
    #         # otherwise causes exit code 135
    #         if q.empty():
    #             sleep(0.001)
    #         data = q.get()
    #         if data is None:
    #             break
    #         else:
    #             doc_id, doc_url, content = data
    #             self.handler.handlePage(doc_id, doc_url, content, self.lock)
    #             self.errorlog.write("test")
    #             print("Handling " + doc_id)

    def startDocument(self):
        print("Started analysing")