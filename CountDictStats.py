__author__ = 'vladimir'
from re import match
from pymorphy2 import MorphAnalyzer


all = 0
nonnum = 0
all_postings = 0
alpha_postings = 0
no_stops_postings = 0
low_reg = dict()
lemmatized = dict()
with open("Dictionary") as f:
    for line in f.readlines():
        all += 1
        word = line.split(" ")[0]
        cnt = int(line.split(" ")[1])
        all_postings += cnt
        if match("^[^\W\d]+$", word):
            nonnum += 1
            alpha_postings += cnt
            lo = word.lower()
            if lo in low_reg:
                low_reg[lo] += cnt
            else:
                low_reg[lo] = cnt
    just_ru = {k: v for (k, v) in low_reg.items() if match(u"^[\u0400-\u0500]+$", k)}
    ru_postings = sum(just_ru.values())
    morph = MorphAnalyzer()
    c = 0
    for k, v in just_ru.items():
        if c % 100000 == 0:
            print(c)
        c += 1
        lem = morph.parse(k)[0].normal_form
        if lem in lemmatized:
            lemmatized[lem] += int(v)
        else:
            lemmatized[lem] = int(v)
    with open("stopwords", "r") as st:
        stops = set(st.read().split('\n'))
        for k, v in just_ru.items():
            if not k in stops:
                no_stops_postings += v
print("Raw dictionary size = {0}\n"
      "Without numbers = {1}\n"
      "Lowered = {2}\n"
      "Just russian = {3}\n".format(all, nonnum, len(low_reg), len(just_ru)))
print("Lemmatized = {0}\n\n".format(len(lemmatized)))
print("All postings = {0}\n"
      "Just alpha = {1}\n"
      "Just russian = {2}\n"
      "No stops = {3}".format(all_postings, alpha_postings, ru_postings, no_stops_postings))
with open("lem_dict", "w") as f:
    for k, v in sorted(lemmatized.items(), reverse=True, key=lambda pair: pair[1]):
        f.write("{0} {1}\n".format(k, v))