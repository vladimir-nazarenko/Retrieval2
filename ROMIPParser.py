__author__ = 'vladimir'
from re import findall
from re import match, sub
from collections import defaultdict
from lxml import html, cssselect, etree
from lxml.etree import ParseError
from lxml.html.clean import Cleaner
from io import StringIO
from urllib.parse import urlparse


# gets and returns information about one single document
class DocumentInfo:
    def __init__(self, doc_id, doc_url, doc_html, cleaner):
        self.features = dict()
        # init class variables
        # text values
        self.features["id"] = doc_id
        self.features["url"] = sub("[\r\n\t]", " ", doc_url)
        self.doc_html = doc_html
        self.doc_url = doc_url
        # representation for html parser
        self.code = html.fromstring(doc_html)
        # try:
        #     self.tree = etree.parse(StringIO(doc_html), etree.HTMLParser())
        # except ParseError:
        #     print("Parse Error in id = {0}".format(doc_id))
        self.cleaner = cleaner
        self.precompute()

    def setTitle(self):
        try:
            tag = self.code.xpath("//title")
            if tag is None:
                self.features["title"] = ""
            else:
                self.features["title"] = sub("[\r\n\t]", " ", tag[0].text)
        except AttributeError:
            print("Problem with title in docid = {0}".format(self.features["id"]))
        except TypeError:
            print("Problem with title in docid = {0}".format(self.features["id"]))
        except IndexError:
            print("Problem with title in docid = {0}".format(self.features["id"]))

    def setTable(self):
        # some bug
        select_tables = cssselect.CSSSelector("table")
        symbol_count = 0
        # print(select_tables(self.code))
        for t in select_tables(self.code):
            cleaned = self.cleaner.clean_html(t)
            txt = sub("[\r\n\t ]", "", cleaned.text_content())
            # print(t)
            # print(txt)
            symbol_count += len(txt)
        if not self.features["size_of_text"] == 0:
            self.features["fraction_of_table"] = float(symbol_count) / self.features["size_of_text"]

    def precompute(self):
        self.features["size_with_markup"] = len(self.doc_html)
        cleaned = self.cleaner.clean_html(self.code)
        txt = cleaned.text_content()
        self.features["text"] = sub("[\r\n\t]", " ", txt)
        list_of_words = findall("[a-zA-Z0-9а-яА-Я\d]+", self.features["text"])
        self.features["length"] = len(list_of_words)
        self.features["size_of_text"] = len(self.features["text"])
        self.setLinks()
        self.setTitle()
        self.setTable()

    def setLinks(self):
        # select = cssselect.CSSSelector("a")
        # all_links = [el.get("href") for el in select(self.tree)]
        all_links = self.code.xpath("//a/@href")
        # split into external and internal and filter out the "#"
        internal = []
        external = []
        base_domain = urlparse(self.doc_url).netloc
        self.features["url_depth"] = len(findall("/", urlparse(self.doc_url).path)) + 1
        for link in all_links:
            p = urlparse(link)
            domain_name = p.netloc
            if not link or match("^#$", link):
                pass
            # internal relative link
            elif base_domain == domain_name or not domain_name:
                internal.append(sub("[\r\n\t]", " ", link))
            else:
                external.append(sub("[\r\n\t]", " ", link))
        self.features["internal_links"] = internal
        self.features["external_links"] = external

    def getDocumentFeatures(self):
        return self.features


class AggregatedStatistics:
    def __init__(self):
        self.correctly_handled_docs = 0
        self.total_word_count = 0
        self.dictionary = defaultdict(int)
        self.watched_document_number = 0
        self.finished = False
        # print("file opened")
        self.output_file = open("collection_task6.tsv", "w")

    # not thread safe
    def feed(self, doc_info):
        # if self.watched_document_number > 10:
        #     self.output_file.close()
        fts = doc_info.getDocumentFeatures()
        feature_list = [fts["id"], fts["url"], fts["title"], fts["text"], fts["length"],
                        fts["size_of_text"] / fts["size_with_markup"], fts["fraction_of_table"], fts["url_depth"],
                        len(fts["internal_links"]) + len(fts["external_links"]),
                        "${0}$".format("|".join(fts["external_links"]))]
        feature_list = [str(x) for x in feature_list]
        line = "\t".join(feature_list)
        self.correctly_handled_docs += 1
        self.output_file.write(line + "\n")

    def __str__(self):
        # return str(self.watched_document_number)
        return "Handled: {0} documents of {1}".format(self.correctly_handled_docs, self.watched_document_number)

    def incrementWatchedDocumentNumber(self):
        self.watched_document_number += 1

    def summarize(self):
        st = "Handled: {0} documents of {1}".format(self.correctly_handled_docs, self.watched_document_number)
        print(st)
        with open("CommonStats", "w") as f:
            f.write(st)
        self.output_file.close()