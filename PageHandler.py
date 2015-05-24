__author__ = 'vladimir'

from time import time, sleep
from ROMIPParser import AggregatedStatistics, DocumentInfo
from base64 import b64decode
from lxml.html.clean import Cleaner
from re import match, findall, IGNORECASE, sub
import sys, traceback
from multiprocessing import Lock
from lxml.etree import ParseError


class PageHandler:
    def __init__(self):
        self.stats = AggregatedStatistics()
        self.cleaner = Cleaner()
        self.cleaner.comments = True
        self.cleaner.style = True
        self.errors = open("errored", "w")
        self.write_lock = Lock()
        self.inf = None

    # the main consumer
    def handlePage(self, doc_id, doc_url, doc_html_enc, lock):
        with lock:
            # print(self.stats.watched_document_number)
            self.stats.incrementWatchedDocumentNumber()
        doc_html = b64decode(doc_html_enc)
        # doc_html = sub(r'[^\x00-\x7fа-яА-Я0-9]+', '*', doc_html.decode("utf-16")).encode("utf-8")
        # try decode
        try:
            html = doc_html.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            try:
                html = doc_html.decode("cp1251", errors="strict")
            except UnicodeDecodeError:
                html = doc_html.decode("utf-8", errors="ignore")
        self.inf = None
        html_without_unicode = sub(r'[^\x00-\x7fа-яА-Я0-9]+', ' ', html)
        try:
            self.inf = DocumentInfo(doc_id, doc_url, html_without_unicode, self.cleaner)
        except ValueError:
            print("Value error in " + doc_id)
            traceback.print_exc(file=sys.stdout)
            return
        except RuntimeError:
            print("Runtime error in", doc_id)
            traceback.print_exc(file=sys.stdout)
            log_info(doc_html, self.write_lock, self.errors, doc_id)
            return
        except ParseError:
            print("Parser error in", doc_id)
            traceback.print_exc(file=sys.stdout)
            log_info(doc_html, self.write_lock, self.errors, doc_id)
            return
        lock.acquire()
        try:
            self.stats.feed(self.inf)
        except KeyError:
            print("Key error in ", doc_id)
            log_info(doc_html, self.write_lock, self.errors, doc_id)
            print("logged")
        except AttributeError:
            print("Couldn't detect encoding of ", doc_id)
            log_info(doc_html, self.write_lock, self.errors, doc_id)
        finally:
            lock.release()


def log_info(info, lock, out, id):
    with lock:
        out.write("ID OF THE DOCUMENT: " + str(id))
        out.write(info.decode())