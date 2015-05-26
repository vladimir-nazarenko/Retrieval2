__author__ = 'vladimir'
from re import match
from collections import defaultdict
from time import time


def stemURL(url):
    return match("(http://)(w{0,3}\.?)([^/]*)", url).group(3)

urls = "links"
# urls = "testLinks"
start = time()
with open(urls, "r") as data:
    bad_chars = "{}\n|"
    index = defaultdict(list)
    cnt = 0
    while True:
        try:
            url_line = data.readline()
            document_links = data.readline()
            if not url_line:
                break
            if len(document_links) == 0:
                continue
            document = stemURL(url_line)
            if len(document) == 0:
                continue
            for u in document_links.split("|"):
                for c in bad_chars:
                    u = u.replace(c, "")
                stripped_url = stemURL(u)
                if not len(stripped_url) == 0 and not stripped_url == document:
                    index[stripped_url].append(document)
            cnt += 1
        except AttributeError:
            continue
    print("Handled {0} documents".format(cnt))
    print("Exceeded {0}".format(time() - start))
    fancy_index = [(key, list(set(lst))) for key, lst in index.items()]
    count_index = [(key, len(value)) for key, value in fancy_index]
    raw_index = list(index.items())
    with open("raw_index", "w") as out:
        for key, value in (sorted(raw_index, key=lambda k: len(k[1]), reverse=True)):
            out.write("{0} {1}\n".format(key, "|".join(value)))
    with open("cited_by", "w") as out:
        for key, value in (sorted(count_index, key=lambda k: k[1], reverse=True)):
            out.write("{0} {1}\n".format(key, value))
    with open("fancy_ind", "w") as out:
        for key, value in (sorted(fancy_index, key=lambda k: len(k[1]), reverse=True)):
            out.write("{0} {1}\n".format(key, "|".join(value)))
    with open("by_row_ind", "w") as out:
        out.write("Target,Source\n")
        for key, value in (sorted(fancy_index, key=lambda k: len(k[1]), reverse=True)):
            for item in value:
                out.write("{0},{1}\n".format(key, item))