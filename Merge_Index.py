import os


i1 = []
i2 = []


def merge_index(index1, index2):           # merges two index files
    with open(index1, 'r') as file:
        holder1 = file.read()

    with open(index2, 'r') as file:
        holder2 = file.read()

    i1 = holder1.split("\n\n")
    i1 = i1[0:len(i1)-1]

    i2 = holder2.split("\n\n")
    i2 = i2[0:len(i2)-1]

    path = os.getcwd()
    path = path + "\merged_index.txt"
    merge = open(path, "w+", encoding='latin-1', errors='ignore')

    index = 0

    while index < len(i1) and index < len(i2):
        if i1[index].split(",")[0] == i2[index].split(",")[0]:
            key = i1[index].split(",")[0]
            document_frequency = int(i1[index].split(",")[1]) + int(i2[index].split(",")[1])
            temp1 = i1[index][i1[index].find(','):]
            temp1 = temp1[i1[index].find(','):]
            temp2 = i2[index][i2[index].find(','):]
            temp2 = temp2[i2[index].find(','):]
            if int(i1[index].split(",")[2]) < int(i2[index].split(",")[2]):
                posting_list = temp1 + temp2
            else:
                posting_list = temp2 + temp1
            merge.write(key+","+str(document_frequency)+posting_list+"\n\n")

        else:
            keys = sorted([i1[index].split(",")[0], i2[index].split(",")[0]])
            if keys[0] == i1[index].split(",")[0]:
                merge.write(i1[index]+"\n\n")
            else:
                merge.write(i2[index]+"\n\n")

        index += 1

    while index < len(i1):
        merge.write(i1[index]+"\n\n")
        index += 1

    while index < len(i2):
        merge.write(i2[index]+"\n\n")
        index += 1

    file.close()
    return


''' Take 2 indexes file at a time to merger them into a single file'''
merge_index("index_1.txt", "index_2.txt")
merge_index("merged_index.txt", "index_3.txt")
