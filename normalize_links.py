__author__ = 'vladimir'

with open("linksasis.txt", "r") as f:
    with open("links", "w") as o:
        while True:
            url_line = f.readline()
            document_links = f.readline()
            if not url_line:
                break
            o.write(url_line)
            links = document_links[1:-2]
            o.write("{" + links + "}\n")