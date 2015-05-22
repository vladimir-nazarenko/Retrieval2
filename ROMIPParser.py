__author__ = 'vladimir'
from re import findall
from re import match
from numpy import mean, nanmean
from collections import defaultdict
from lxml import html, cssselect
from lxml.html.clean import Cleaner
import operator


# gets and returns information about one single document
class DocumentInfo:
    def __init__(self, doc_id, doc_url, doc_html):
        # init class variables
        self.doc_id = doc_id
        self.doc_url = doc_url
        self.doc_html = doc_html
        self.mean_word_length = None
        self.number_of_words = None
        self.size_with_markup = None
        self.size_of_text = None
        self.links = None
        # representation for html parser
        self.code = html.fromstring(self.doc_html, self.doc_url)
        self.raw_text = None
        # set of words and numbers
        self.raw_dictionary = None
        self.precompute()

    def precompute(self):
        self.setLinks()
        self.setDictionary()
        self.size_with_markup = len(self.doc_html)
        self.size_of_text = len(self.raw_text)

    def setLinks(self):
        select = cssselect.CSSSelector("a")
        links = filter(lambda el: not el is None, [el.get("href") for el in select(self.code)])
        self.links = list(filter(lambda link: match("http.*", link), links))

    # handles mean word length, number of words, raw text and raw dictionary
    def setDictionary(self):
        cleaner = Cleaner()
        cleaner.javascript = True
        cleaner.style = True
        cleaner.comments = True
        try:
            cleaned = cleaner.clean_html(self.code)
            self.raw_text = cleaned.text_content()
            # regex filters numbers from words
            list_of_words = findall("[a-zA-Z0-9а-яА-Я\d]+", self.raw_text)
            self.number_of_words = len(list_of_words)
            lst = list(map(lambda word: len(word), list_of_words))
            self.mean_word_length = mean(lst)
            self.raw_dictionary = set(list_of_words)
        except RuntimeError:
            raise ValueError

    def sizeWithMarkup(self):
        return self.size_with_markup

    def sizeOfText(self):
        return self.size_of_text

    def meanWordLength(self):
        return self.mean_word_length

    def numberOfWords(self):
        return self.number_of_words

    def rawDictionary(self):
        return self.raw_dictionary


class AggregatedStatistics:
    def __init__(self):
        self.correctly_handled_docs = 0
        self.raw_sizes = []
        self.text_sizes = []
        self.word_numbers = []
        self.avg_word_lengths = []
        self.total_word_count = 0
        self.dictionary = defaultdict(int)
        self.watched_document_number = 0
        self.finished = False
        self.links_file = open("links", "w")
        self.heaps_law = open("heaps", "w")

    # not thread safe
    def feed(self, doc_info):
        self.raw_sizes.append(doc_info.sizeWithMarkup())
        self.text_sizes.append(doc_info.sizeOfText())
        self.word_numbers.append(doc_info.numberOfWords())
        self.avg_word_lengths.append(doc_info.meanWordLength())
        self.total_word_count += doc_info.numberOfWords()
        self.correctly_handled_docs += 1
        for word in doc_info.raw_dictionary:
            self.dictionary[word] += 1
        if not doc_info.links is None and len(doc_info.links) > 0:
            self.links_file.write(doc_info.doc_url + "{" + "|".join(doc_info.links) + "}\n")
        self.heaps_law.write("[" + str(len(self.dictionary)) + "," + str(self.total_word_count) + "] ")

    def __str__(self):
        return "Handled: {0} documents of {1}".format(self.correctly_handled_docs, self.watched_document_number)

    def writeDictionary(self, fileName):
        with open(fileName, "w") as f:
            dic = sorted(self.dictionary.items(), key=operator.itemgetter(1), reverse=True)
            joined_tuples = map(lambda pair: "{0} {1}".format(pair[0], pair[1]), dic)
            s = "\n".join(joined_tuples)
            f.write(s)

    def incrementWatchedDocumentNumber(self):
        self.watched_document_number += 1

    def summarize(self):
        st = "Handled: {0} documents of {1}\n" \
             "Avg word length: {2} \n" \
             "Total word count: {3}\n" \
             "Avg raw size: {4}\n" \
             "Avg text size: {5}\n" \
             "Avg length in words: {6}".format(self.correctly_handled_docs, self.watched_document_number,
                                               nanmean(list(filter(lambda v: v is not None, self.avg_word_lengths))),
                                               self.total_word_count,
                                               mean(list(filter(lambda v: v is not None, self.raw_sizes))),
                                               mean(list(filter(lambda v: v is not None, self.text_sizes))),
                                               mean(list(filter(lambda v: v is not None, self.word_numbers)))
                                               )
        print(st)
        with open("CommonStats", "w") as f:
            f.write(st)
        self.heaps_law.close()
        self.links_file.close()
        self.writeDictionary("Dictionary")