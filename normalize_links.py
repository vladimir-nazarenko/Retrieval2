__author__ = 'vladimir'

with open("linksasis.txt", "r") as f:
    with open("links", "w") as o:
        while True:
            url_line = f.readline()
            document_links = f.readline()
            if not url_line:
                break
            urls = url_line[1:-2]
            o.write("{" + urls + "}\n")