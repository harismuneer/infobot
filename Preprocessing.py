import os
from bs4 import BeautifulSoup, NavigableString, Tag
import re


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
    original_path = os.getcwd()
    new_folder = original_path + "\parsed"
    try:
        os.mkdir(new_folder)
    except OSError:
        print("Creation of the directory %s failed" % new_folder)
    else:
        print("Successfully created the directory %s " % new_folder)

    new_folder = new_folder + "/"+folder
    try:
        os.mkdir(new_folder)
    except OSError:
        print("Creation of the directory %s failed" % new_folder)
    else:
        print("Successfully created the directory %s " % new_folder)
    data_set = "\corpus1/" + folder
    path = original_path + data_set
    for files in os.listdir(path):
            if '.txt' not in files:
                file_name = "/" + files
                new_path = path + file_name
                text = parse_html(new_path)
                if text is not None and len(text) is not 0:
                    parsed_file = new_folder+file_name
                    file = open(parsed_file, "w+", encoding="iso-8859-1", errors='ignore')
                    file.write(text)
                else:
                    print(files + "has no text")


allow = True
while allow:
    directory = input("Select a directory out of 1, 2 or 3\n")
    if directory is "1" or directory is "2" or directory is "3":
        allow = False
        pre_processing(directory)
