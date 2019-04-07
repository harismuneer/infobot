
import sys
import time

sys.path.append('./')

from preprocess_and_index import preprocess_text
from encoding_utilities import make_posting_dic
from encoding_utilities import decompress_posting_list

from nltk.stem import PorterStemmer

from collections import OrderedDict



##################################################################
##################################################################

def create_uncompressed_index():
    # reading the index_file and making an in_memory index from in order to answer queries faster
    # (we can also read the index_file line by line and save the posting lists with matching terms but this isn't efficient)
    index_file = open("./index_files/uncompressed/inverted_index.txt", "r", encoding="utf-8")

    index_data = index_file.readlines()
    index_file.close()

    # creating index as a hash-map
    inverted_index = dict()

    for x in index_data:
        posting_list = x.rstrip().split(",")
        term = posting_list[0]

        inverted_index[term] = make_posting_dic(posting_list[1:])

    return inverted_index


##################################################################
##################################################################

def create_compressed_index_vocab():
    index_vocab = open("./index_files/compressed/inverted_index_vocab.txt", "r", encoding="utf-8")

    # read complete vocab and then using the offsets read only relevant posting lists
    vocab_data = index_vocab.readlines()

    # create a hash-map for vocab for faster retrieval of posting list offsets
    vocab = OrderedDict()

    for i in range(len(vocab_data)):
        term, offset = vocab_data[i].rstrip().split(",")

        vocab[term] = (i, int(offset))

    index_vocab.close()

    return vocab

##################################################################
##################################################################

def load_complete_compressed_index(vocab):
    vocab_indexes = [x for x in vocab.keys()]

    index_postings = open("./index_files/compressed/inverted_index_postings.txt", "rb")

    inverted_index = dict()

    for t in vocab.keys():

        index1, offset1 = vocab[t]

        # read required posting list
        try:
            offset2 = vocab[vocab_indexes[index1 + 1]][1]
            encoded_posting = index_postings.read(int(offset2) - int(offset1))
        except:
            encoded_posting = index_postings.read(int(offset1))

        original_posting_list = decompress_posting_list(encoded_posting)

        inverted_index[t] = original_posting_list

    index_postings.close()

    return inverted_index



##################################################################
##################################################################

# assuming only EXACT Match retrieval is required

def boolean_retrieval(query, inverted_index, compressed):

    if not compressed:

        relevant_documents = set()

        for k in range(len(query)):

            if query[k] not in inverted_index:
                break

            if k == 0:
                relevant_documents = set(inverted_index[query[0]][1].keys())

            else:
                # retrieve all document_ids from this posting list
                document_ids = set(inverted_index[query[k]][1].keys())

                relevant_documents = relevant_documents.intersection(document_ids)

        return relevant_documents

    else:
        vocab = inverted_index
        vocab_indexes = [x for x in vocab.keys()]

        index_postings = open("./index_files/compressed/inverted_index_postings.txt", "rb")

        relevant_documents = set()

        for k in range(len(query)):

            if query[k] not in vocab:
                break

            index1, offset1 = vocab[query[k]]

            # for quick access to the required posting list
            index_postings.seek(int(offset1), 0)

            # read required posting list
            try:
                offset2 = vocab[vocab_indexes[index1+1]][1]
                encoded_posting = index_postings.read(int(offset2) - int(offset1))
            except:
                encoded_posting = index_postings.read(int(offset1))

            original_posting_list = decompress_posting_list(encoded_posting)

            if k == 0:
                relevant_documents = set(original_posting_list[1].keys())

            else:
                document_ids = set(original_posting_list[1].keys())

                relevant_documents = relevant_documents.intersection(document_ids)

        index_postings.close()

        return relevant_documents


##################################################################
##################################################################

def main():


    ################################################################
    ################################################################

    doc_ids_data = open("doc_info.txt", "r").readlines()

    doc_ids = dict()

    for x in doc_ids_data:
        x = x.rstrip().split(",")

        doc_ids[int(x[0])] = x[1]

    ################################################################
    ################################################################

    query = input("Enter Query: ")

    # read stop words
    with open("./stop_list.txt", "r") as file:
        stop_words = file.readlines()
        stop_words = [x.strip() for x in stop_words]

    # initialize stemmer
    ps = PorterStemmer()

    # preprocess the query
    query = preprocess_text(query, ps, stop_words)

    ################################################################
    ################################################################

    # get document ids which contain all words present in the query

    # do retrieval with uncompressed index

    start_time = time.clock()

    uncompressed_index = create_uncompressed_index()

    doc_results = boolean_retrieval(query, uncompressed_index, compressed=False)

    print("\nTime to load complete Uncompressed Index and then do retrieval: %.2f seconds" % (time.clock() - start_time))


    print("\n--------------------------------------")
    print("Uncompressed Index Results:\n")

    if len(doc_results) != 0:
        # map document ids back to their original names
        results = [doc_ids[x] for x in doc_results]
        results = sorted(results)


        for doc in results:
            print(doc)

    else:
        print("\nNo result found.")

    print("--------------------------------------")

    ################################################################
    ################################################################

    start_time = time.clock()

    compressed_index_vocab = create_compressed_index_vocab()

    # do retrieval with compressed index
    doc_results = boolean_retrieval(query, compressed_index_vocab, compressed=True)

    print("\nTime to load complete vocab and partial posting lists and then retrieve"
          " using Compressed Index: %.2f seconds" % (time.clock() - start_time))

    print("\n--------------------------------------")
    print("Compressed Index Results:\n")

    if len(doc_results) != 0:
        # map document ids back to their original names
        results = [doc_ids[x] for x in doc_results]
        results = sorted(results)

        for doc in results:
            print(doc)
    else:
        print("\nNo result found.")

    print("--------------------------------------")


    ################################################################
    ################################################################

    start_time = time.clock()

    compressed_index_vocab = create_compressed_index_vocab()
    complete_index = load_complete_compressed_index(compressed_index_vocab)

    # do retrieval with compressed index
    doc_results = boolean_retrieval(query, complete_index, compressed=False)

    print("\nTime to load complete vocab and posting lists and then retrieve"
          " using Compressed Index: %.2f seconds" % (time.clock() - start_time))

    print("\n--------------------------------------")
    print("Compressed Index Results:\n")

    if len(doc_results) != 0:
        # map document ids back to their original names
        results = [doc_ids[x] for x in doc_results]
        results = sorted(results)

        for doc in results:
            print(doc)
    else:
        print("\nNo result found.")

    print("--------------------------------------")




##################################################################
##################################################################

if __name__ == '__main__':
    # get things rolling
    main()


