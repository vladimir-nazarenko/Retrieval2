__author__ = 'vladimir'
from lxml import html
from lxml.html.clean import Cleaner
from lxml import etree, cssselect
from io import StringIO
from re import match, findall
from urllib.parse import urlparse

with open("test.html", "r") as f:
    txt = f.read()
    # html = html.fromstring(txt)
    # cleaner = Cleaner()
    # cleaner.javascript = True
    # cleaner.comments = True
    # cleaner.style = True
    # cleaned = cleaner.clean_html(html)
    # t = html.open_in_browser
    # for e in t:
    #     print(e.text)
    #print(cleaned.text_content())
    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(txt), parser)
    result = etree.tostring(tree.getroot(), method="html")
    # title
    print(tree.getroot().find("head/title").text)
    htm = html.fromstring(etree.tostring(tree.getroot().find("body")))
    cleaner = Cleaner()
    cleaner.javascript = True
    cleaner.comments = True
    cleaner.style = True
    cleaned = cleaner.clean_html(htm)
    # body text
    # print(cleaned.text_content())
    # links
    sel = cssselect.CSSSelector("a")
    code = html.fromstring(txt)
    all_links = [el.get("href") for el in sel(tree)]
    # split into external and internal and filter out the "#"
    internal = []
    external = []
    filtered = []
    for link in all_links:
        p = urlparse(link)
        domain_name = p.netloc
        if match("^#$", link) or not link:
            filtered.append(link)
        # internal relative link
        elif match("habrahabr.ru", domain_name) or not domain_name:
            internal.append(link)
        else:
            external.append(link)
    print("internal", internal)
    print("external", external)
    print("filtered", filtered)
    sl = cssselect.CSSSelector("tr")
    print(sl(code)[0].text_content()) # get length from here
    # print(urlparse(internal[20]).path)
    # print(len(findall("[^/]?/", "")) + 1)