import os
from bs4 import BeautifulSoup, NavigableString, Tag
import nltk
from nltk.stem import PorterStemmer
import re
from collections import defaultdict


final_tokens = []
doc_id = []
file_token = []


def create_folder(des):    # create any folder
    try:
        os.mkdir(des)
    except OSError:
        print("Creation of the directory %s failed" % des)
    else:
        print("Successfully created the directory %s " % des)


def parse_html(html):       # ignoring headers and HTML Tag to extract document text
    f = open(html, "r", encoding='iso-8859-1', errors='ignore')
    soup = BeautifulSoup(f, 'html.parser')
    # Ignore anything in head
    body, text = soup.body, []
    if body is not None:
        for element in body.descendants:
            # We use type and not isinstance since comments, cdata, etc are subclasses that we don't want
            if type(element) == NavigableString:
                parent_tags = (t for t in element.parents if type(t) == Tag)
                hidden = False
                for parent_tag in parent_tags:
                    # Ignore any text inside a non-displayed tag
                    # We also behave is if scripting is enabled (noscript is ignored)
                    # The list of non-displayed tags and attributes from the W3C specs:
                    if (parent_tag.name in ('area', 'base', 'basefont', 'datalist', 'head', 'link',
                                            'meta', 'noembed', 'noframes', 'param', 'rp', 'script',
                                            'source', 'style', 'template', 'track', 'title', 'noscript') or
                            parent_tag.has_attr('hidden') or
                            (parent_tag.name == 'input' and parent_tag.get('type') == 'hidden')):
                        hidden = True
                        break
                if hidden:
                    continue

                # remove any multiple and leading/trailing whitespace
                string = ' '.join(element.string.split())
                if string:
                    if element.parent.name == 'a':
                        a_tag = element.parent
                        # replace link text with the link
                        if 'href' in a_tag:
                            string = a_tag['href']
                            # concatenate with any non-empty immediately previous string
                            if (type(a_tag.previous_sibling) == NavigableString and
                                    a_tag.previous_sibling.string.strip()):
                                text[-1] = text[-1] + ' ' + string
                                continue
                        elif element.previous_sibling and element.previous_sibling.name == 'a':
                            text[-1] = text[-1] + ' ' + string
                            continue
                    elif element.parent.name == 'p':
                        # Add extra paragraph formatting newline
                        string = '\n' + string
                    text += [string]
        doc = '\n'.join(text)
        doc = re.sub(r'^https?:\/\/.*[\r\n]*', '', doc, flags=re.MULTILINE)
        return doc
    return


def find_all(a_string, sub):     # to find token in text obtained
    result = []
    k = 0
    while k < len(a_string):
        k = a_string.find(sub, k)
        if k == -1:
            return result
        else:
            result.append(k)
            k += 1                                                          # change to k += len(sub) to not search overlapping results
    return result


def pre_processing(folder):
    ps = PorterStemmer()                                            # initialize stemmer
    original_path = os.getcwd()                                     # receive working directory path
    stop_words = original_path+"\stoplist.txt"                      # reading stoplist path
    stops = [line.rstrip('\n') for line in open(stop_words)]        # adding all stop words in list after reading stoplist file
    data_set = "\corpus1/" + folder
    path = original_path + data_set                                 # opening folder(1/2/3) from corpus folder
    docpath = original_path +"\doc_id"+folder+".txt"
    with open(docpath, 'r') as docfile:
        holder1 = docfile.read()
    id = holder1.split("\n")
    id = id[0:len(id)-1]
    for ids in id:
        doc_id.append(ids.split(":")[1])
    for files in os.listdir(path):                                  # picking all files in the folder one by one
            tokenize = {}
            tt = []
            if '.txt' not in files:                                 # ignoring redundant files
                file_name = "/" + files
                new_path = path + file_name
                text = parse_html(new_path)                         # parse HTML file
                if text is not None and len(text) is not 0:         # if text obtained, then proceed
                    text = text.lower()
                    tokens = nltk.word_tokenize(text)               # Split text to tokens
                    for i in range(0, len(tokens)):
                        tokens[i] = tokens[i].lower()               # converting all tokens' case to lower case
                        tokens[i] = re.sub(r"[^a-zA-Z]+", "", tokens[i])
                    tokens = [token.rstrip('\n') for token in tokens]
                    tokens = list(set(tokens))
                    for token in tokens:
                        if token.isalpha() is False:
                            tokens.remove(token)
                    tokens = [token for token in tokens if token not in stops]
                    if tokens is not None:
                        for token in tokens:
                            if len(token) > 0:
                                st = ps.stem(token)
                                if st not in stops:
                                    arr = find_all(text, st)        # recording positions
                                    if len(arr) is not 0:
                                        tokenize[st] = arr
                                        tt.append(st)
                        final_tokens.append(tokenize)
                        file_token.append(tt)


def create_index(data):                 # create index using dict from tokens obtained
    index = defaultdict(list)
    for idx, text in enumerate(data):
        for word in text:
            index[word].append(idx)
    return index


def create_inverted_index(folder):      # create inverted index
    original_path = os.getcwd()                                             # get present working directory path
    file_path = original_path + "/index_" + folder + ".txt"                 # name a text file after folder (1/2/3)
    inv_index = create_index(file_token)                                    # call to create index using dict after obtaining tokens                                        # sorting key alphabetically
    file = open(file_path, "w+", encoding='latin-1', errors='ignore')       # writing posting list in file acc. to format
    for key in sorted(inv_index.keys()):
        file.write(key)                                                     # write term
        file.write(",")
        file.write(str(len(inv_index[key])))                                # write total number doc. in which it occurs
        for doc in inv_index[key]:
            file.write(",")
            file.write(str(doc_id[doc]))                                    # write doc id
            file.write(",")
            find = final_tokens[doc]
            arr = find[key]
            file.write(str(len(arr)))                                       # write doc. freq.
            file.write(",")
            for i in range(0, len(arr)):                                    # write doc. positions
                file.write(str(arr[i]))
                if i is not (len(arr)-1):
                    file.write(",")
        file.write("\n\n")
    file.close()
    return


''' Takes input for folder 1, 2 or 3 to begin with pre-processing'''
allow = True
while allow:    # if wrong input given
    directory = input("Select a directory out of 1, 2 or 3\n")
    if directory is "1" or directory is "2" or directory is "3":
        allow = False
        pre_processing(directory)       # begin with pre_processing'''
        create_inverted_index(directory)
