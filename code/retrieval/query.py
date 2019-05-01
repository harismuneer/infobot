import sys
from xml.dom import minidom

from nltk.stem import PorterStemmer

sys.path.append('../index/')

from preprocess_and_index import preprocess_text

import math


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


# Function to calculate document frequency for a term, documents having that term and frequency of the term in every document

def calculate_dft(query):
    # Initialization
    dft = 0  # Document Frequency for a term( no of documents, having a term)
    doc = []  # contains documents' ID having a term
    freq = []  # contains frequency of term for all documents stored in doc[] list

    # Reading MERGED UNCOMPRESSED INDEX
    f = open("inverted_index.txt", "r", encoding="utf-8")
    lines = f.readlines()

    # Performing calculations
    for line in lines:
        line = line.split(',')
        if query == line[0]:
            dft += int(line[1])
            doc.append(line[2])
            freq.append(line[3])
            j = 2
            j = j + 1 + int(freq[len(freq) - 1]) + 1
            while j < len(line):
                doc.append(line[j])
                freq.append(line[j + 1])
                j = j + 1 + int(freq[len(freq) - 1]) + 1

    return dft, doc, freq


##################################################################
##################################################################


# Calculating value of ct for Okapi-TF computation

def calculate_ct(dft, n):
    # n is number of total documents and dft is number of documents having a term
    ct = (n - dft) + 0.5
    ct = ct / (dft + 0.5)
    ct = math.log(ct)
    return ct


##################################################################
##################################################################


# Calculating score for Okapi-TF

def okapi_tf(q, ids):
    # constant values
    k1 = 1
    b = 1.5

    # Initialization
    ld = []  # contains length for every document
    lave = 0  # average length of all documents

    # Reading document_information file for fetching req. information
    f = open("doc_info.txt", "r")
    information = f.readlines()

    # Finding length of every document
    for info in information:
        info = info.split(",")
        ld.append(int(info[2].replace('\n', '')))

    # Calculating average length of documents
    for length in ld:
        lave += length
    lave = lave / len(ld)

    # Open run.txt file for storing scoring results
    file = open("run.txt", "w+")

    # Loop to run for all Queries
    for i in range(0, len(q)):

        # Initialization for every Query
        query = q[i]
        topic = ids[i]
        dft_of_terms_in_query = []  # contains document frequency for all terms in a query
        ct_of_terms_in_query = []  # contains ct for all terms in a query
        doc_having_terms = []  # contains blocks of documents having terms in a query
        frequency_of_terms_in_docs = []  # contains blocks of freq. of doc_having_terms
        document_scores = []  # contains score of every document for a query
        rank = []  # contains rank of every document for a query

        add = 0
        while add < len(ld):
            document_scores.append(0)
            rank.append(0)
            add += 1

        # Getting Values for Calculation
        for qu in query:
            x, y, z = calculate_dft(qu)
            dft_of_terms_in_query.append(x)
            doc_having_terms.append(y)
            frequency_of_terms_in_docs.append(z)
            ct_of_terms_in_query.append(calculate_ct(dft_of_terms_in_query[len(dft_of_terms_in_query) - 1], len(ld)))

        # Applying Okapi-TF Formulae
        for index in range(0, len(query)):
            document = doc_having_terms[index]
            frequency = frequency_of_terms_in_docs[index]
            for d in range(0, len(document)):
                numerator = (k1 + 1) / int(frequency[d])
                denominator = (k1 * ((k1 + 1) + b * (ld[d] / lave))) + int(frequency[d])
                result = numerator / denominator
                document_scores[int(document[d]) - 1] += round(ct_of_terms_in_query[index] * result, ndigits=2)

        # Ordering scores in descending order to keep track of documents with highest to lowest score(0)
        score = list(dict.fromkeys(document_scores))
        score = sorted(score, reverse=True)

        # Assigning Rank to a score
        for d in range(0, len(document_scores)):
            rank[d] = score.index(document_scores[d]) + 1

        # Finding Lowest Rank
        limit = max(rank)

        # Writing run.txt- document with highest rank(1) appears first and then so on
        for r in range(1, limit + 1):

            # finding documents with same rank
            dc = [m for m, val in enumerate(rank) if val == r]

            # fetching info about that document from doc_info.txt read above
            for l in range(0, len(dc)):
                for info in information:
                    info = info.split(",")
                    info1 = info[1]
                    info1 = info1.split("/")
                    if info[0] == str(dc[l] + 1):
                        file.write(
                            str(topic) + " 0 " + info1[3] + " " + str(r) + " " + str(document_scores[dc[l]]) + "\n")

    return


##################################################################
##################################################################


# Function to calculate Inverse Document Frequency

def calculate_idf(dft, n):
    # n is total number of doc. and dft is no. of documents containing term
    idf = math.log(n / dft)
    return idf


##################################################################
##################################################################


# Function to calculate Vector-Space Score

def vector_space(q, ids):
    # Open run.txt file for storing scoring results
    file = open("run.txt", "w")

    # Reading document_information file for fetching required information
    f = open("doc_info.txt", "r")
    information = f.readlines()

    # Initialization
    length = []

    # Finding length of every document
    for info in information:
        info = info.split(",")
        length.append(int(info[2].replace('\n', '')))

    # Loop to run for all queries
    for i in range(0, len(q)):

        # Initialization
        query = q[i]
        topic = ids[i]
        tfidf_for_every_document = []  # contains block of tf-idf for every document
        doc_having_terms = []  # contains blocks of documents having terms present in a query
        tfidf_of_doc_having_terms = []  # contains blocks of tf-idf of documents present in doc_having_terms
        tfiqf_for_query = []  # contains tf-iqf of terms present in a query
        document_scores = []  # contains score of all documents for a query
        rank = []  # contains rank of all documents for a query

        add = 0
        while add < len(length):
            document_scores.append(0)
            rank.append(0)
            add += 1

        for term in range(0, len(query)):
            x, y, z = calculate_dft(query[term])
            idf_of_terms_in_query = (calculate_idf(x, len(length)))
            doc_having_terms.append(y)
            for j in range(0, len(z)):
                z[j] = int(z[j]) * idf_of_terms_in_query
            tfidf_of_doc_having_terms.append(z)
            temp = []
            add = 0
            while add < len(length):
                temp.append(0)
                add += 1
            doc = doc_having_terms[len(doc_having_terms) - 1]
            weight = tfidf_of_doc_having_terms[len(tfidf_of_doc_having_terms) - 1]
            for j in range(0, len(doc)):
                temp[int(doc[j]) - 1] += weight[j]
            tfidf_for_every_document.append(temp)

            # Calculating weights of terms in Query!
            idfq = math.log(len(query) / query.count(query[term]))
            tfiqf = (query.count(query[term]) / len(query)) * idfq
            tfiqf_for_query.append(tfiqf)

            for index in range(0, len(document_scores)):
                document_scores[index] += round((tfiqf_for_query[len(tfiqf_for_query) - 1] * temp[index]), ndigits=2)

        # Divide score of document with length to find real score
        for index in range(0, len(document_scores)):
            if length[index] is not 0:
                document_scores[index] = round(document_scores[index] / length[index], ndigits=2)

        # Ordering scores in descending order to keep track of documents with highest to lowest score(0)
        score = list(dict.fromkeys(document_scores))
        score = sorted(score, reverse=True)

        # Assigning Rank to a score
        for d in range(0, len(document_scores)):
            rank[d] = score.index(document_scores[d]) + 1

        # Finding Lowest Rank
        limit = max(rank)

        # Writing run.txt- document with highest rank(1) appears first and then so on
        for r in range(1, limit + 1):

            # finding documents with same rank

            dc = [m for m, val in enumerate(rank) if val == r]
            for l in range(0, len(dc)):

                # fetching info about that document from doc_info.txt read above
                for info in information:
                    info = info.split(",")
                    info1 = info[1]
                    info1 = info1.split("/")
                    if info[0] == str(dc[l] + 1):
                        file.write(
                            str(topic) + " 0 " + info1[3] + " " + str(r) + " " + str(document_scores[dc[l]]) + "\n")

    return


##################################################################
##################################################################


def main():

    score = sys.argv[1]
    run_id = sys.argv[2]

    queries = fetch_queries()

    if score == "okapi-tf":
        # calculate Okapi-TF Score
        okapi_tf(queries, run_id)

    elif score == "vector-space":
        # calculate Vector-Space Score
        vector_space(queries, run_id)

    else:
        # Wrong scoring method
        print("Invalid Scoring Function!")
        print("Exiting...")

    return


if __name__ == '__main__':
    # get things rolling
    main()
