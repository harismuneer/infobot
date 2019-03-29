import os
from bs4 import BeautifulSoup, NavigableString, Tag
import re

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

doc_id = []
path = os.getcwd()
file = open(path + "\Additional_Info.txt", "w+", encoding='latin-1', errors='ignore')

docpath = path +"\doc_id1"+".txt"
with open(docpath, 'r') as docfile:
    holder1 = docfile.read()
id = holder1.split("\n")
id = id[0:len(id)-1]
for ids in id:
    doc_id.append(ids.split(":")[1])

docpath = path +"\doc_id2"+".txt"
with open(docpath, 'r') as docfile:
    holder1 = docfile.read()
id = holder1.split("\n")
id = id[0:len(id)-1]
for ids in id:
    doc_id.append(ids.split(":")[1])

docpath = path +"\doc_id3"+".txt"
with open(docpath, 'r') as docfile:
    holder1 = docfile.read()
id = holder1.split("\n")
id = id[0:len(id)-1]
for ids in id:
    doc_id.append(ids.split(":")[1])

j = 0
path = path + '/corpus1/1/'
for files in os.listdir(path):
    if '.txt' not in files:
        file_name = "/" + files
        new_path = path + file_name
        text = parse_html(new_path)                         # parse HTML file
        if text is not None and len(text) is not 0:
            file.write(str(doc_id[j]))
            file.write(",1/"+files+",")
            file.write(str(len(text))+"\n")
        j += 1

path = os.getcwd()
path = path + '/corpus1/2/'
for files in os.listdir(path):
    if '.txt' not in files:
        file_name = "/" + files
        new_path = path + file_name
        text = parse_html(new_path)                         # parse HTML file
        if text is not None and len(text) is not 0:
            file.write(str(doc_id[j]))
            file.write(",2/"+files+",")
            file.write(str(len(text))+"\n")
        j += 1

path = os.getcwd()
path = path + '/corpus1/3/'
for files in os.listdir(path):
    if '.txt' not in files:
        file_name = "/" + files
        new_path = path + file_name
        text = parse_html(new_path)                         # parse HTML file
        if text is not None and len(text) is not 0:
            file.write(str(doc_id[j]))
            file.write(",3/"+files+",")
            file.write(str(len(text))+"\n")
        j += 1

file.close()
