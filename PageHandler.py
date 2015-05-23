__author__ = 'vladimir'

from time import time, sleep
from ROMIPParser import AggregatedStatistics, DocumentInfo
from base64 import b64decode
from lxml.html.clean import Cleaner


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
        try:
            inf = DocumentInfo(doc_id, doc_url, str(doc_html, "utf-8"), self.cleaner)
        except UnicodeDecodeError:
            try:
                inf = DocumentInfo(doc_id, doc_url, str(doc_html, "cp1251"), self.cleaner)
            except UnicodeDecodeError:
                print("Encoding error on " + doc_id)
                return
            except ValueError:
                print("Unicode symbols in " + doc_id)
                return
            except RuntimeError:
                print("Runtime error in", doc_id)
                return
        except ValueError:
            print("Unicode symbols in " + doc_id)
            return
        except RuntimeError:
            print("Runtime error in", doc_id)
            return
        lock.acquire()
        try:
            self.stats.feed(inf)
        except KeyError:
            print("Key error in ", doc_id)
        finally:
            lock.release()

