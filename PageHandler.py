__author__ = 'vladimir'

from time import time, sleep
from ROMIPParser import AggregatedStatistics, DocumentInfo
from base64 import b64decode
from lxml.html.clean import Cleaner
from re import match, findall, IGNORECASE


class PageHandler:
    def __init__(self):
        self.stats = AggregatedStatistics()
        self.cleaner = Cleaner()
        self.cleaner.comments = True
        self.cleaner.style = True

    # the main consumer
    def handlePage(self, doc_id, doc_url, doc_html_enc, lock):
        with lock:
            # print(self.stats.watched_document_number)
            self.stats.incrementWatchedDocumentNumber()
        doc_html = b64decode(doc_html_enc)
        # doc_html = sub(r'[^\x00-\x7fа-яА-Я0-9]+', '*', doc_html.decode("utf-16")).encode("utf-8")
        inf = None
        try:
            try_decode = doc_html.decode("utf-8", errors="ignore")
            # print(try_decode)
            if findall("charset ?= ?utf-?8", try_decode, IGNORECASE):
                inf = DocumentInfo(doc_id, doc_url, try_decode, self.cleaner)
            else:
                try_decode = doc_html.decode("cp1251", errors="ignore")
                if findall("charset ?= ?windows-1251", try_decode, IGNORECASE):
                    inf = DocumentInfo(doc_id, doc_url, try_decode, self.cleaner)
        except UnicodeDecodeError:
            print("Encoding error on " + doc_id)
            return
        except ValueError:
            print("Value error in " + doc_id)
            return
        except RuntimeError:
            print("Runtime error in", doc_id)
            return
        lock.acquire()
        try:
            self.stats.feed(inf)
        except KeyError:
            print("Key error in ", doc_id)
        except AttributeError:
            print("Couldn't detect encoding of ", doc_id)
        finally:
            lock.release()

