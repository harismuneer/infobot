import sys
import time

sys.path.append('./')

from encoding_utilities import compress_posting_list
from encoding_utilities import decompress_posting_list
from encoding_utilities import make_posting_dic

##################################################################
##################################################################

def merge_posting_lists(p1, p2):

    result = list()

    # add doc_freq of both posting lists
    result.append(p1[0] + p2[0])

    new_posting_list = dict()
    [new_posting_list.update(d) for d in (p1[1], p2[1])]


    # convert the new posting list into a comma separated list
    for d_id in sorted(new_posting_list.keys()):
        result.append(d_id)

        term_freq = new_posting_list[d_id][0]
        result.append(term_freq)

        for i in range(term_freq):
            result.append(new_posting_list[d_id][1][i])

    return result

##################################################################
##################################################################


# takes two index files and merges them into one
def merge_index(index1_name, index2_name, merged_index_name, compressed):

    ################################################################
    ################################################################

    # code to merge uncompressed indexes
    if not compressed:

        # open relevant files
        index1 = open(index1_name, "r", encoding="utf-8")
        index2 = open(index2_name, "r", encoding="utf-8")
        new_index = open(merged_index_name, "w", encoding="utf-8")

        posting1 = index1.readline().rstrip().split(",")
        posting2 = index2.readline().rstrip().split(",")

        while posting1[0] != "" and posting2[0] != "":
            if posting1[0] == posting2[0]:

                term = posting1[0]

                posting1 = make_posting_dic(posting1[1:])
                posting2 = make_posting_dic(posting2[1:])

                # merge both posting lists into one
                merged_posting_list = merge_posting_lists(posting1, posting2)
                merged_posting_list = [str(x) for x in merged_posting_list]

                new_index.write(term + "," + ",".join(merged_posting_list) + "\n")

                # read next posting list for both indexes
                posting1 = index1.readline().rstrip().split(",")
                posting2 = index2.readline().rstrip().split(",")

            elif posting1[0] < posting2[0]:
                new_index.write(",".join(posting1) + "\n")

                # read next posting list for 1st index
                posting1 = index1.readline().rstrip().split(",")

            else:
                new_index.write(",".join(posting2) + "\n")

                # read next posting list for 2nd index
                posting2 = index2.readline().rstrip().split(",")


        while posting1[0] != "":
            new_index.write(",".join(posting1) + "\n")
            posting1 = index1.readline().rstrip().split(",")


        while posting2[0] != "":
            new_index.write(",".join(posting2) + "\n")
            posting2 = index2.readline().rstrip().split(",")

        index1.close()
        index2.close()
        new_index.close()

    ################################################################
    ################################################################

    # code to merge compressed indexes
    else:
        # open relevant files
        index1_vocab = open(index1_name + "_vocab.txt", "r", encoding="utf-8")
        index1_posting = open(index1_name + "_postings.txt", "rb")

        index2_vocab = open(index2_name + "_vocab.txt", "r", encoding="utf-8")
        index2_posting = open(index2_name + "_postings.txt", "rb")

        new_index_vocab = open(merged_index_name + "_vocab.txt", "w", encoding="utf-8")
        new_index_posting = open(merged_index_name + "_postings.txt", "wb")


        index1_t1, index1_o1 = index1_vocab.readline().rstrip().split(",")
        index1_t2, index1_o2 = index1_vocab.readline().rstrip().split(",")

        index2_t1, index2_o1 = index2_vocab.readline().rstrip().split(",")
        index2_t2, index2_o2 = index2_vocab.readline().rstrip().split(",")

        posting1 = index1_posting.read(int(index1_o2) - int(index1_o1))
        posting2 = index2_posting.read(int(index2_o2) - int(index2_o1))

        byte_offset = 0

        while posting1 and posting2:

            if index1_t1 == index2_t1:

                posting1 = decompress_posting_list(posting1)
                posting2 = decompress_posting_list(posting2)

                # merge both posting lists into one
                merged_posting_list = merge_posting_lists(posting1, posting2)
                merged_posting_list = make_posting_dic(merged_posting_list)

                merged_posting_list = compress_posting_list(merged_posting_list)

                new_index_vocab.write(index1_t1 + "," + str(byte_offset) + "\n")
                byte_offset += new_index_posting.write(merged_posting_list)

                # read next posting list for both indexes
                try:
                    index1_t1, index1_o1 = index1_t2, index1_o2
                    index1_t2, index1_o2 = index1_vocab.readline().rstrip().split(",")
                    posting1 = index1_posting.read(int(index1_o2) - int(index1_o1))
                except:
                    posting1 = index1_posting.read()

                try:
                    index2_t1, index2_o1 = index2_t2, index2_o2
                    index2_t2, index2_o2 = index2_vocab.readline().rstrip().split(",")
                    posting2 = index2_posting.read(int(index2_o2) - int(index2_o1))
                except:
                    posting2 = index2_posting.read()


            elif index1_t1 < index2_t1:
                new_index_vocab.write(index1_t1 + "," + str(byte_offset) + "\n")
                byte_offset += new_index_posting.write(posting1)

                try:
                    # read next posting list for 1st index
                    index1_t1, index1_o1 = index1_t2, index1_o2
                    index1_t2, index1_o2 = index1_vocab.readline().rstrip().split(",")
                    posting1 = index1_posting.read(int(index1_o2) - int(index1_o1))
                except:
                    posting1 = index1_posting.read()

            else:
                new_index_vocab.write(index2_t1 + "," + str(byte_offset) + "\n")
                byte_offset += new_index_posting.write(posting2)

                try:
                    # read next posting list for 2nd index
                    index2_t1, index2_o1 = index2_t2, index2_o2
                    index2_t2, index2_o2 = index2_vocab.readline().rstrip().split(",")
                    posting2 = index2_posting.read(int(index2_o2) - int(index2_o1))
                except:
                    posting2 = index2_posting.read()

        while posting1:
            new_index_vocab.write(index1_t1 + "," + str(byte_offset) + "\n")
            byte_offset += new_index_posting.write(posting1)

            try:
                # read next posting list for 1st index
                index1_t1, index1_o1 = index1_t2, index1_o2
                index1_t2, index1_o2 = index1_vocab.readline().rstrip().split(",")
                posting1 = index1_posting.read(int(index1_o2) - int(index1_o1))
            except:
                posting1 = index1_posting.read()

        while posting2:
            new_index_vocab.write(index2_t1 + "," + str(byte_offset) + "\n")
            byte_offset += new_index_posting.write(posting2)

            try:
                # read next posting list for 1st index
                index2_t1, index2_o1 = index2_t2, index2_o2
                index2_t2, index2_o2 = index2_vocab.readline().rstrip().split(",")
                posting2 = index2_posting.read(int(index2_o2) - int(index2_o1))
            except:
                posting2 = index2_posting.read()

        # close files
        index1_vocab.close()
        index2_vocab.close()
        new_index_vocab.close()

        index1_posting.close()
        index2_posting.close()
        new_index_posting.close()


    print("\n------------------------------------------------------")
    print("Successfully Merged " + index1_name + " and " + index2_name)
    print("------------------------------------------------------")


##################################################################
##################################################################

def main():

    ##################################################################
    start_time = time.clock()

    merge_index("./index_files/uncompressed/index_1.txt", "./index_files/uncompressed/index_2.txt",
                "./index_files/uncompressed/intermediate_index.txt", compressed=False)

    merge_index("./index_files/uncompressed/intermediate_index.txt", "./index_files/uncompressed/index_3.txt",
                "./index_files/uncompressed/inverted_index.txt", compressed=False)

    print("\nTime taken to merge Uncompressed Indexes: %.2f seconds" % (time.clock() - start_time))
    ##################################################################

    ##################################################################

    start_time = time.clock()

    merge_index("./index_files/compressed/index_1", "./index_files/compressed/index_2",
                "./index_files/compressed/intermediate_index", compressed=True)

    merge_index("./index_files/compressed/intermediate_index", "./index_files/compressed/index_3",
                "./index_files/compressed/inverted_index", compressed=True)

    print("\nTime taken to merge Compressed Indexes: %.2f seconds" % (time.clock() - start_time))

    ##################################################################


##################################################################
##################################################################

if __name__ == '__main__':
    # get things rolling
    main()
