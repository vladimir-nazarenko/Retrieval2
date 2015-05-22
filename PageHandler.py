__author__ = 'vladimir'

from time import time, sleep
from ROMIPParser import AggregatedStatistics, DocumentInfo
from base64 import b64decode


class PageHandler:
    def __init__(self):
        self.stats = AggregatedStatistics()

    # the main consumer
    def handlePage(self, doc_id, doc_url, doc_html_enc, lock):
        with lock:
            self.stats.incrementWatchedDocumentNumber()
        doc_html = b64decode(doc_html_enc)
        try:
            inf = DocumentInfo(doc_id, doc_url, str(doc_html, "utf-8"))
        except UnicodeDecodeError:
            try:
                inf = DocumentInfo(doc_id, doc_url, str(doc_html, "cp1251"))
            except UnicodeDecodeError:
                print("Encoding error on " + doc_id)
                return
            except ValueError:
                print("Unicode symbols in " + doc_id)
                return
        except ValueError:
            print("Unicode symbols in " + doc_id)
            return
        lock.acquire()
        try:
            self.stats.feed(inf)
        except:
            print("Exception in lock")
        finally:
            lock.release()

