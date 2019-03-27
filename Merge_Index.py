import os


def merge_index(index1, index2):           # merges two index files
    path = os.getcwd()
    path = path + "\merged_index.txt"
    merge = open(path, "w+", encoding='latin-1', errors='ignore')
    with open(index1, 'r') as file:
        holder1 = file.read()

    with open(index2, 'r') as file:
        holder2 = file.read()

    while len(holder1) is not 0 and len(holder2) is not 0:
        read_buffer1 = holder1.split("\n\n")[0]
        read_buffer2 = holder2.split("\n\n")[0]
        if read_buffer1.split(",")[0] == read_buffer2.split(",")[0]:   # if same keys found
            key = read_buffer1.split(",")[0]
            document_frequency = int(read_buffer1.split(",")[1]) + int(read_buffer2.split(",")[1])
            temp1 = read_buffer1[read_buffer1.find(','):]
            temp1 = temp1[read_buffer1.find(','):]
            temp2 = read_buffer2[read_buffer2.find(','):]
            temp2 = temp2[read_buffer2.find(','):]
            if int(read_buffer1.split(",")[2]) < int(read_buffer2.split(",")[2]):
                posting_list = temp1+temp2
            else:
                posting_list = temp2+temp1

            merge.write(key+","+str(document_frequency)+posting_list+"\n\n")
            # read next keys from both files
            holder1 = holder1.replace(read_buffer1+"\n\n", '')
            holder2 = holder2.replace(read_buffer2+"\n\n", '')
        else:

            keys = sorted([read_buffer1.split(",")[0], read_buffer2.split(",")[0]])
            if keys[0] == read_buffer1.split(",")[0]:
                merge.write(read_buffer1+"\n\n")
                holder1 = holder1.replace(read_buffer1+"\n\n", '')
            else:
                merge.write(read_buffer2+"\n\n")
                holder2 = holder2.replace(read_buffer2+"\n\n", '')

    while len(holder1) is not 0:
        read_buffer1 = holder1.split("\n\n")[0]
        merge.write(read_buffer1+"\n\n")
        holder1 = holder1.replace(read_buffer1+"\n\n", '')

    while len(holder2) is not 0:
        read_buffer2 = holder2.split("\n\n")[0]
        merge.write(read_buffer2+"\n\n")
        holder2 = holder2.replace(read_buffer2+"\n\n", '')
    file.close()
    return


''' Take 2 indexes file at a time to merger them into a single file'''
merge_index("index_1.txt", "index_2.txt")
