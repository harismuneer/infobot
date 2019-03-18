import os
from collections import defaultdict


def create_folder(des):
    try:
        os.mkdir(des)
    except OSError:
        print("Creation of the directory %s failed" % des)
    else:
        print("Successfully created the directory %s " % des)


def create_index(data):
    index = defaultdict(list)
    for idx, text in enumerate(data):
        for word in text:
            index[word].append(idx)
    return index


def create_inverted_index(folder):
    tokens_sub_directory = []
    original_path = os.getcwd()
    file_path = original_path+"\indexing"
    create_folder(file_path)
    file_path = file_path + "/index_" + folder + ".txt"
    data_path = original_path +"\pre_process/"+folder
    for files in os.listdir(data_path):
        path = data_path+"/" + files
        tokens_one_doc = [line.rstrip('\n') for line in open(path, errors='ignore', encoding='latin-1')]
        for token in tokens_one_doc:
            if token is ' ' or token is '--':
                tokens_one_doc.remove(token)
        tokens_sub_directory.append(tokens_one_doc)
    inv_index = create_index(tokens_sub_directory)
    file = open(file_path, "w+", encoding='latin-1', errors='ignore')
    for key in inv_index.keys():
        term = key
        file.write(key)
        file.write(",")
        doc_freq = len(inv_index[key])
        file.write(str(doc_freq))
        file.write(",")
        file.write("\n")
    file.close()
    '''for key in inv_index.keys():
        term = key
        doc_freq = len(inv_index[key])
        print("TERM:" + term)
        print("DOC_FREQ:")
        print(doc_freq)
        for doc in inv_index[key]:
            print("DOC_ID:")
            print(doc)
            track = tokens_sub_directory[doc]
            for name in track:
                if name is term:
                    print(name)'''
    return


create_inverted_index("3")

