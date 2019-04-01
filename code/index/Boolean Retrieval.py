import os
import nltk


def extract_info(folder, tokens):
    doc_id = []
    doc_name = []
    path = os.getcwd()

    # Checking Index_1.txt
    file = path + '/index_' + folder + '.txt'
    with open(file, 'r') as file:
        index = file.read()

    keys = index.split("\n\n")
    keys = keys[0:len(keys)-1]

    for token in tokens:
        for key in keys:
            if token == key.split(",")[0]:
                term_info = key.split(",")
                term_info = term_info[0:len(term_info)-1]
                term = term_info[0]
                doc_id.append(term_info[2])
                info = 3
                while info < len(term_info):
                    info = info + int(term_info[info])+1
                    if info < (len(term_info)):
                        doc_id.append(term_info[info])
                        info += 1

        file = path + '\doc_id' + folder + '.txt'
        with open(file, 'r') as file:
            holder = file.read()

        holder = holder.split("\n")
        holder = holder[0:len(holder)-1]
        for hold in holder:
            hold = hold.split(":")
            for dc_id in doc_id:
                if dc_id == hold[1]:
                    doc_name.append(hold[0])
        for name in doc_name:
            print(folder+'/'+name)
    return len(doc_name)


def boolean_retrieval(text):

    tokens = nltk.word_tokenize(text)
    for i in range(0, len(tokens)):
        tokens[i] = tokens[i].lower()
    count = 0
    count += extract_info("1", tokens)
    count += extract_info("2", tokens)
    count += extract_info("3", tokens)
    if count is 0:
        print('No Result Found!')
    return




query = input("Write the Query:\n")
boolean_retrieval(query)
