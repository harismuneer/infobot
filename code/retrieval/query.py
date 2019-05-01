import sys
from xml.dom import minidom

from nltk.stem import PorterStemmer

sys.path.append('../index/')
sys.path.append('./')

from preprocess_and_index import preprocess_text
from boolean_retrieval import create_compressed_index_vocab
from boolean_retrieval import decompress_posting_list

import math


##################################################################
##################################################################

def get_encoded_posting_list(vocab, vocab_indexes, index_postings, term):
    # get posting list for this term and decompress it
    index1, offset1 = vocab[term]

    # for quick access to the required posting list
    index_postings.seek(int(offset1), 0)

    # read required posting list
    try:
        offset2 = vocab[vocab_indexes[index1 + 1]][1]
        encoded_posting = index_postings.read(int(offset2) - int(offset1))
    except:
        encoded_posting = index_postings.read(int(offset1))

    return encoded_posting


##################################################################
##################################################################


# Function to fetch the queries from topics.xml and pre process them
def fetch_queries():
    # Initialization
    ps = PorterStemmer()
    queries = dict()  # will contain queries

    # read stop words
    with open("../index/stop_list.txt", "r") as file:
        stop_words = file.readlines()
        stop_words = [x.strip() for x in stop_words]

    t_file = minidom.parse("./topics.xml")

    # Get Queries
    elements = t_file.getElementsByTagName('topic')

    for elem in elements:
        query_data = elem.getElementsByTagName('query')[0].firstChild.data

        query_data = preprocess_text(query_data, ps, stop_words)

        queries[elem.attributes['number'].value] = query_data

    return queries


##################################################################
##################################################################


# Write Scores to File
def write_scores(scores, run_id):
    r_file = open("run" + run_id + ".txt", "w")

    for query in scores.keys():

        doc_scores = scores[query]

        doc_scores = sorted(doc_scores.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)

        for i in range(len(doc_scores)):
            r_file.write(str(query) + " 0 " + doc_scores[i][0] + " " + str(doc_scores[i][1]) + " " + str(
                i + 1) + " " + "run" + str(run_id) + "\n")

    r_file.close()


##################################################################
##################################################################


# Calculating score for Okapi-TF

def okapi_tf(queries, doc_info):
    vocab = create_compressed_index_vocab()
    vocab_indexes = [x for x in vocab.keys()]

    index_postings = open("../index/index_files/compressed/inverted_index_postings.txt", "rb")

    # total number of docs
    total_docs = len(doc_info.keys())

    # calculate average length
    length_sum = 0
    for l in doc_info.values():
        length_sum += int(l[1])

    l_ave = length_sum/total_docs

    k1 = 1
    b = 1.5

    query_doc_scores = dict()

    for query_id in queries.keys():

        query = queries[query_id]

        doc_scores = dict()

        for k in range(len(query)):
            encoded_posting = get_encoded_posting_list(vocab, vocab_indexes, index_postings, query[k])
            original_posting_list = decompress_posting_list(encoded_posting)

            df = original_posting_list[0]
            ct = math.log((total_docs - df + 0.5)/(df + 0.5))

            for doc in original_posting_list[1].keys():
                tf = original_posting_list[1][doc][0]
                weight_d_q = ((k1 + 1)*tf)/(k1*((1-b)+b*(float(doc_info[doc][1])/l_ave))+tf)

                doc_scores[doc] = doc_scores.get(doc, 0) + (ct * weight_d_q)

        ##################################################################

        # map document ids back to their original names and skip docs with zero score
        doc_name_scores = dict()

        for d in doc_scores.keys():
            d_score = round(doc_scores[d], ndigits=2)

            if d_score != 0:
                doc_name_scores[doc_info[d][0]] = d_score

        ##################################################################

        query_doc_scores[query_id] = doc_name_scores

    index_postings.close()

    return query_doc_scores

##################################################################
##################################################################

# Function to calculate Vector-Space Score
def vector_space(queries, doc_info):
    vocab = create_compressed_index_vocab()
    vocab_indexes = [x for x in vocab.keys()]

    index_postings = open("../index/index_files/compressed/inverted_index_postings.txt", "rb")

    total_docs = len(doc_info.keys())

    query_doc_scores = dict()

    for query_id in queries.keys():

        query = queries[query_id]

        doc_scores = dict()

        for k in range(len(query)):
            encoded_posting = get_encoded_posting_list(vocab, vocab_indexes, index_postings, query[k])
            original_posting_list = decompress_posting_list(encoded_posting)

            # calculate weight (term count) of a query term
            weight_t_q = query.count(query[k])

            df = original_posting_list[0]
            idf = math.log(total_docs / df)

            for doc in original_posting_list[1].keys():
                tf = original_posting_list[1][doc][0]
                weight_d_q = tf * idf

                doc_scores[doc] = doc_scores.get(doc, 0) + (weight_t_q * weight_d_q)

        ##################################################################

        # Divide score of document with length to find real score
        for d in doc_scores.keys():
            doc_scores[d] = round(doc_scores[d] / float(doc_info[d][1]), ndigits=2)

        ##################################################################

        # map document ids back to their original names and skip docs with zero score
        doc_name_scores = dict()

        for d in doc_scores.keys():
            if doc_scores[d] != 0:
                doc_name_scores[doc_info[d][0]] = doc_scores[d]

        ##################################################################

        query_doc_scores[query_id] = doc_name_scores

    index_postings.close()

    return query_doc_scores


##################################################################
##################################################################


def main():
    score = sys.argv[1]
    run_id = sys.argv[2]

    # get queries
    queries = fetch_queries()

    ################################################################
    ################################################################

    # get document ids
    doc_ids_data = open("../index/doc_info.txt", "r").readlines()

    doc_ids = dict()

    for x in doc_ids_data:
        x = x.rstrip().split(",")

        doc_ids[int(x[0])] = (x[1], x[2])

    ################################################################
    ################################################################

    # if score == "okapi-tf":
    if True:
        # calculate Okapi-TF Score
        query_doc_scores = okapi_tf(queries, doc_ids)

        # write scores to file
        write_scores(query_doc_scores, run_id)

    # elif score == "vector-space":
    if True:
        run_id = "2"
        # calculate Vector-Space Score
        query_doc_scores = vector_space(queries, doc_ids)

        # write scores to file
        write_scores(query_doc_scores, run_id)

    else:
        # Wrong scoring method
        print("Invalid Scoring Function!")
        print("Exiting...")

    ################################################################
    ################################################################


if __name__ == '__main__':
    # get things rolling
    main()
