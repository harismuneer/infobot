import os
import string
import sys
import time

from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer

sys.path.append('./')

from encoding_utilities import compress_posting_list
##################################################################
##################################################################

# returns document text
def get_text(html):
    tree = BeautifulSoup(html, 'lxml')

    body = tree.body

    if body is None:
        return None

    # ignore script and style tags
    for tag in body.select('script'):
        tag.decompose()

    for tag in body.select('style'):
        tag.decompose()

    text = body.get_text(separator='\n')
    return text


##################################################################
##################################################################

# returns tokens after pre-processing
def preprocess_text(text, stemmer, stop_words):
    # remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))

    # make tokens
    text = text.split()

    # remove words which contain any character other than alphabets
    text = [x for x in text if x.isalpha()]

    # convert to lower-case
    text = [x.lower() for x in text]

    # ignore stop words
    text = [x for x in text if x not in stop_words]

    # stem words
    text = [stemmer.stem(x) for x in text]

    return text


##################################################################
##################################################################

def main():
    main_path = "./corpus/%d/"

    doc_id = 1

    # file containing docIDS
    doc_info = open("doc_info.txt", "w")

    # read stop words
    with open("./stop_list.txt", "r") as file:
        stop_words = file.readlines()
        stop_words = [x.strip() for x in stop_words]

    # initialize stemmer
    ps = PorterStemmer()

    # directory for indexes
    if not os.path.exists('./index_files'):
        os.makedirs('./index_files')

    for i in range(3):

        sub_directory = main_path % (i + 1)

        print("\n-------------------------------------------------------------------")
        print("Processing Sub Directory", sub_directory)
        print("-------------------------------------------------------------------")

        ##################################################################
        ##################################################################

        """######################### PRE-PROCESSING ########################"""

        start_time = time.clock()

        # tokens dictionary
        doc_tokens = dict()

        # id of first doc in sub_directory
        local_id_first = doc_id

        # picking all files in the folder one by one
        for f_name in os.listdir(sub_directory):

            try:
                # open document
                doc_file = open(sub_directory + f_name, "rb")

                # read complete document
                f_text = doc_file.read()

                # remove headers
                w_header, html_head, html_body = f_text.split(b'\r\n\r\n', maxsplit=2)

                html = html_body.strip()

                if len(html) == 0:
                    continue

                # get document text
                text = get_text(html)

                # pre-process text
                text = preprocess_text(text, ps, stop_words)

                # add to tokens dictionary
                doc_tokens[doc_id] = text

                # write docID
                doc_info.write(str(doc_id) + "," + sub_directory + f_name + "," + str(len(text)) + "\n")
                doc_id += 1

                print(f_name)

                # close document file
                doc_file.close()

            except:
                pass

        print("\nTime taken to pre-process files in " + sub_directory + " : %.2f seconds" % (time.clock() - start_time))


        ##################################################################
        ##################################################################

        start_time = time.clock()

        """######################### INDEX CREATION ########################"""

        print("-----------------------------------------")
        print("Creating Index...")

        index = dict()

        # id of last doc in sub_directory
        local_id_last = doc_id - 1

        # make index
        for d_id in range(local_id_first, local_id_last + 1):

            for j in range(len(doc_tokens[d_id])):
                term = doc_tokens[d_id][j]

                if term not in index:
                    index[term] = list()
                    index[term].append(0)
                    index[term].append(dict())

                if d_id not in index[term][1]:
                    index[term][1][d_id] = list()
                    index[term][1][d_id].append(0)
                    index[term][1][d_id].append(list())

                    index[term][0] += 1  # increment document frequency (df)

                index[term][1][d_id][1].append(j + 1)
                index[term][1][d_id][0] += 1  # increment term frequency (tf)

        # Index Format:
        # <term t>,<df>,<docID>,<tf>,<pos1>,<pos2>,<pos3>…,<docID>,<tf>,<pos1>,<pos2>,<pos3>…,

        print("\nTime taken to create index : %.2f seconds" % (time.clock() - start_time))

        ##################################################################
        ##################################################################

        start_time = time.clock()

        """######################### UNCOMPRESSED INDEX ########################"""

        # directory for uncompressed indexes
        uncompressed_index_dir = "./index_files/uncompressed"

        if not os.path.exists(uncompressed_index_dir):
            os.makedirs(uncompressed_index_dir)

        index_file_name = uncompressed_index_dir + "./index_%s.txt" % str(i + 1)
        index_file = open(index_file_name, "w", encoding="utf-8")

        # writing index
        for term in sorted(index.keys()):
            doc_freq = str(index[term][0])

            index_file.write(term + "," + doc_freq)

            for d_id in sorted(index[term][1].keys()):
                index_file.write("," + str(d_id))

                term_freq = str(index[term][1][d_id][0])

                index_file.write("," + term_freq)

                for term_pos in index[term][1][d_id][1]:
                    index_file.write("," + str(term_pos))

            index_file.write("\n")

        index_file.close()

        print("\nUncompressed Index for Directory %d created successfully!!" % (i+1))

        print("\nTime taken to write uncompressed index: %.2f seconds" % (time.clock() - start_time))

        ##################################################################
        ##################################################################

        """######################### COMPRESSED INDEX ########################"""

        start_time = time.clock()

        # directory for compressed indexes
        compressed_index_dir = "./index_files/compressed"

        if not os.path.exists(compressed_index_dir):
            os.makedirs(compressed_index_dir)

        # vocab file
        com_index_vocab = compressed_index_dir + "./index_%s_vocab.txt" % str(i + 1)
        com_index_vocab_file = open(com_index_vocab, "w", encoding="utf-8")

        # postings file
        com_index_posting = compressed_index_dir + "./index_%s_postings.txt" % str(i + 1)
        com_index_posting_file = open(com_index_posting, "wb")

        byte_offset = 0

        # compress index
        for term in sorted(index.keys()):

            posting_list = index[term]

            v_encoded_posting_list = compress_posting_list(posting_list)

            # write v_encoded_posting_list to compressed_index_file
            com_index_vocab_file.write(term + "," + str(byte_offset) + "\n")
            byte_offset += com_index_posting_file.write(v_encoded_posting_list)


        com_index_vocab_file.close()
        com_index_posting_file.close()

        print("\nCompressed Index for Directory %d created successfully!" % (i+1))

        print("\nTime taken to encode and write compressed index: %.2f seconds" % (time.clock() - start_time))


    doc_info.close()


##################################################################
##################################################################

if __name__ == '__main__':
    # get things rolling
    main()
