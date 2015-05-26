__author__ = 'vladimir'

import pymysql
from xml.etree import ElementTree
from collections import defaultdict


# Function generates the file of the following structure, defined in the file learning_feature_specification.txt
def generate_trec_data2008(judgement_file, index):
    # stores the text of the query for each query id
    task_queries = dict()
    queries = ElementTree.parse("queries/web2008_adhoc.xml")
    root = queries.getroot()
    for ch in root:
        if ch.tag.endswith("task"):
            task_queries[int(ch.attrib["id"][3:])] = ch[0].text

    # key is the query id, value is the list of document features list
    # contains relevance judgements
    doc_features = defaultdict(dict)
    judgements_xml = ElementTree.parse(judgement_file)
    root = judgements_xml.getroot()
    for ch in root:
        if ch.tag.endswith("task"):
            for judgement in ch:
                doc_rel = judgement.attrib["relevance"]
                if doc_rel == "vital":
                    rel = 2
                elif doc_rel == "relevant":
                    rel = 1
                elif doc_rel == "notrelevant":
                    rel = 0
                elif doc_rel == "cantbejudged":
                    rel = -1
                else:
                    raise Exception("Undefined relevance: " + doc_rel)
                query_id = int(ch.attrib["id"][3:])
                url = judgement.attrib["id"]
                features = {"url": url, "relevance": rel}
                doc_features[query_id][url] = features
    doc_retrieved = defaultdict(list)
    db = pymysql.connect(host="127.0.0.1", port=9306)
    cur = db.cursor()
    # get feature vector
    # list of ranking expressions to use in sphinx search
    rank_exprs = ["bm25", "sum(tf_idf)", "sum(hit_count)"]
    for task in doc_features.keys():
        # features from title
        for ranker in rank_exprs:
            for part in ["title", "content"]:
                query_string = "select url, weight() from {1} where match('@({3}){0}') limit 20 option ranker=expr('{2}')"\
                    .format("|".join(task_queries[task].split()), index, ranker, part)
                normal_string = query_string.replace("/", "\\\\/").replace("!", "\\\\!").replace("-", "").encode("utf8")
                cur.execute(normal_string)
                # cur stores the list of tuples
                for row in cur:
                    url = row[0]
                    weight = row[1]
                    if url in doc_features[task].keys():
                        # add feature for the document "url" in the query "task"
                        # print(ranker)
                        doc_features[task][url][part + ranker] = weight

    with open("train_set_2008", "w") as f:
        for task, docs in sorted(doc_features.items(), key=lambda pair: pair[0]):
            for url, features in docs.items():
                cnt = 1
                result = []
                for ranker in rank_exprs:
                    for part in ["title", "content"]:
                        if part + ranker in features.keys():
                            result.append(str(cnt) + ":" + str(features[part + ranker]))
                        cnt += 1
                if not len(result) == 0:
                    f.write("{0} qid:{1} {2}#{3}\n".format(features["relevance"],
                                                           task, " ".join(result), features["url"]))


def generate_trec_data2009(judgement_file, index):
    # stores the text of the query for each query id
    task_queries = dict()
    queries = ElementTree.parse("queries/web2008_adhoc.xml")
    root = queries.getroot()
    for ch in root:
        if ch.tag.endswith("task"):
            task_queries[int(ch.attrib["id"][3:])] = ch[0].text

    # key is the query id, value is the list of document features list
    # contains relevance judgements
    doc_features = defaultdict(dict)
    judgements_xml = ElementTree.parse(judgement_file)
    root = judgements_xml.getroot()
    for ch in root:
        if ch.tag.endswith("task"):
            for judgement in ch:
                doc_rel = judgement.attrib["relevance"]
                if doc_rel == "vital":
                    rel = 2
                elif doc_rel == "relevant":
                    rel = 1
                elif doc_rel == "notrelevant":
                    rel = 0
                elif doc_rel == "cantbejudged":
                    rel = -1
                else:
                    raise Exception("Undefined relevance: " + doc_rel)
                query_id = int(ch.attrib["id"][3:])
                doc_id = judgement.attrib["id"]
                features = {"doc_id": doc_id, "relevance": rel}
                doc_features[query_id][doc_id] = features
    doc_retrieved = defaultdict(list)
    db = pymysql.connect(host="127.0.0.1", port=9306)
    cur = db.cursor()
    # get feature vector
    # list of ranking expressions to use in sphinx search
    rank_exprs = ["bm25", "sum(tf_idf)", "sum(hit_count)"]
    for task in doc_features.keys():
        # features from title
        for ranker in rank_exprs:
            for part in ["title", "content"]:
                query_string = "select id, weight() from {1} where match('@({3}){0}') limit 20 option ranker=expr('{2}')"\
                    .format("|".join(task_queries[task].split()), index, ranker, part)
                normal_string = query_string.replace("/", "\\\\/").replace("!", "\\\\!").replace("-", "").encode("utf8")
                cur.execute(normal_string)
                # cur stores the list of tuples
                for row in cur:
                    doc_id = row[0]
                    weight = row[1]
                    if doc_id in doc_features[task].keys():
                        # add feature for the document "url" in the query "task"
                        # print(ranker)
                        doc_features[task][doc_id][part + ranker] = weight

    with open("test_set_2009", "w") as f:
        for task, docs in sorted(doc_features.items(), key=lambda pair: pair[0]):
            for doc_id, features in docs.items():
                cnt = 1
                result = []
                for ranker in rank_exprs:
                    for part in ["title", "content"]:
                        if part + ranker in features.keys():
                            result.append(str(cnt) + ":" + str(features[part + ranker]))
                        cnt += 1
                if not len(result) == 0:
                    f.write("{0} qid:{1} {2}#{3}\n".format(features["relevance"],
                                                           task, " ".join(result), features["doc_id"]))
if __name__ == '__main__':
    names = ["or"]
    for name in ["queries/2008{0}_relevant-minus_table.xml".format(n) for n in names]:
        generate_trec_data2008(name, "morph")
    for name in ["queries/2009{0}_relevant-minus_table.xml".format(n) for n in names]:
        generate_trec_data2008(name, "morph")