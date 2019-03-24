import os
from collections import defaultdict


def create_folder(des):    # create any folder
    try:
        os.mkdir(des)
    except OSError:
        print("Creation of the directory %s failed" % des)
    else:
        print("Successfully created the directory %s " % des)


def create_index(data):                 # create index using dict from tokens obtained
    index = defaultdict(list)
    for idx, text in enumerate(data):
        for word in text:
            index[word].append(idx)
    return index


def create_inverted_index(folder):      # create inverted index
    tokens_sub_directory = []                                               # list to take all tokens in 1/2/3 folder
    doc_ID = []                                                             # store document_ID's prsent in corpus/(1/2/3)
    original_path = os.getcwd()                                             # get present working directory path
    file_path = original_path+"\indexing/"                                  # make a folder to store index of each folder
    create_folder(file_path)
    file_path = file_path + "/index_" + folder + ".txt"                     # name a text file after folder (1/2/3)
    data_path = original_path +"\pre_process/"+folder                       # reading tokens
    for files in os.listdir(data_path):
        path = data_path+"/" + files
        doc_ID.append(files[17:])                                           # extracting document id
        tokens_one_doc = [line.rstrip('\n') for line in open(path, errors='ignore', encoding='latin-1')]  # reading all tokens in list
        for token in tokens_one_doc:
            if token is ' ' or token is '--':
                tokens_one_doc.remove(token)
        tokens_sub_directory.append(tokens_one_doc)
    inv_index = create_index(tokens_sub_directory)                          # call to create index using dict after obtaining tokens
    file = open(file_path, "w+", encoding='latin-1', errors='ignore')       # writing posting list in file acc. to format
    for key in inv_index.keys():
            file.write(key)                                                     # write term
            file.write(",")
            file.write(str(len(inv_index[key])))                                # write total number doc. in which it occurs
            for doc in inv_index[key]:
                file.write(",")
                pos = []
                file.write(str(doc_ID[doc]))                                    # write doc id
                file.write(",")
                track = tokens_sub_directory[doc]
                for i in range(0, len(track)) :
                    if track[i] == key:
                        pos.append(i)
                file.write(str(len(pos)))                                      # write frequency of term in that doc.
                file.write(",")
                for i in range(0, len(pos)):
                    file.write(str(pos[i]))                                    # write positions in document
                    if i is not (len(pos)-1):
                        file.write(",")
            file.write("\n\n")
    file.close()
    return


''' Call all directories one by one for index creation'''
create_inverted_index("1")
create_inverted_index("2")
create_inverted_index("3")


