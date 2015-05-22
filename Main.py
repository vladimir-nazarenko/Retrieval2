__author__ = 'vladimir'
# procedures for xml parsing
from xml.sax import parse
# my classes with defined behavior for parser
from ContentRetriever import ContentRetriever
from PageHandler import PageHandler
# for timing of execution
from time import time

fileName = "big_by.xml"
# fileName = "test_by.xml"
handler = ContentRetriever(PageHandler())
f = open(fileName, encoding="cp1251")
now = time()
print("Started at" + str(now))
try:
    parse(f, handler)
finally:
    print("Finished at " + str(time()))
    print("Elapsed " + str(time() - now))
    f.close()