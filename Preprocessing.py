import os
from bs4 import BeautifulSoup, NavigableString, Tag
import nltk
from nltk.stem import PorterStemmer
import re


def create_folder(des):
    try:
        os.mkdir(des)
    except OSError:
        print("Creation of the directory %s failed" % des)
    else:
        print("Successfully created the directory %s " % des)


def parse_html(html):
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

    return None


def pre_processing(folder):
    ps = PorterStemmer()
    original_path = os.getcwd()
    stop_words = original_path+"\stoplist.txt"
    stops = [line.rstrip('\n') for line in open(stop_words)]

    pre_process_folder = original_path + "\pre_process"
    create_folder(pre_process_folder)
    pre_process_folder = pre_process_folder + "/"+folder
    create_folder(pre_process_folder)
    data_set = "\corpus1/" + folder
    path = original_path + data_set
    for files in os.listdir(path):
            if '.txt' not in files:
                file_name = "/" + files
                new_path = path + file_name
                text = parse_html(new_path)
                if text is not None and len(text) is not 0:
                    tokens = nltk.word_tokenize(text)
                    for i in range(0, len(tokens)):
                        tokens[i] = tokens[i].lower()
                    tokens = [token.rstrip('\n') for token in tokens]
                    for token in tokens:
                        if token in stops:
                            tokens.remove(token)
                    if tokens is not None:
                        for i in range(0, len(tokens)):
                            tokens[i] = ps.stem(tokens[i])
                        for token in tokens:
                            if token in stops:
                                tokens.remove(token)
                        if tokens is not None:
                            pre_process_file = pre_process_folder+file_name
                            file = open(pre_process_file, "w+", encoding='latin-1', errors='ignore')
                            for token in tokens:
                                regex = re.compile('[@_!#$%^&*()<>?/\|}{~:.,;]')
                                if regex.search(token) is None:
                                    file.write(token+"\n")


allow = True
while allow:
    directory = input("Select a directory out of 1, 2 or 3\n")
    if directory is "1" or directory is "2" or directory is "3":
        allow = False
        pre_processing(directory)
