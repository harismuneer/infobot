def merge_index(index1, index2):           # merges two index files

    path = "merged_index.txt"
    merge = open(path, "w+", encoding='latin-1', errors='ignore')
    with open(index1, 'r') as file1, open(index2, 'r') as file2:
        r_buffer1 = file1.readline()
        r_buffer2 = file2.readline()
        while r_buffer1 and r_buffer2:
            if r_buffer1.split(",")[0] == r_buffer2.split(",")[0]:
                key = r_buffer1.split(",")[0]
                document_frequency = int(r_buffer1.split(",")[1]) + int(r_buffer2.split(",")[1])
                temp1 = r_buffer1[r_buffer1.find(','):]
                temp1 = temp1[r_buffer1.find(','):]
                temp2 = r_buffer2[r_buffer2.find(','):]
                temp2 = temp2[r_buffer2.find(','):]
                while r_buffer1[len(r_buffer1)-1] is not '\n':
                    r_buffer1 = file1.readline()
                    temp = r_buffer1[r_buffer1.find(','):]
                    temp = temp[r_buffer1.find(','):]
                    temp1 = temp1 + temp
                temp1 = temp1[: len(temp1)-1]
                while r_buffer2[len(r_buffer2)-1] is not '\n':
                    r_buffer2 = file2.readline()
                    temp = r_buffer2[r_buffer2.find(','):]
                    temp = temp[r_buffer2.find(','):]
                    temp2 = temp2 + temp
                temp2 = temp2[: len(temp2)-1]
                posting = temp1 + temp2
                merge.write(key+","+str(document_frequency)+posting+"\n")
            else:
                keys = sorted([r_buffer1.split(",")[0], r_buffer2.split(",")[0]])
                if keys[0] == r_buffer1.split(",")[0]:
                    merge.write(r_buffer1)
                    while r_buffer1[len(r_buffer1)-1] is not '\n':
                        r_buffer1 = file1.readline()
                        merge.write(r_buffer1)
                else:
                    merge.write(r_buffer2)
                    while r_buffer2[len(r_buffer2)-1] is not '\n':
                        r_buffer2 = file2.readline()
                        merge.write(r_buffer2)
            r_buffer1 = file1.readline()
            r_buffer2 = file2.readline()
        while r_buffer1:
            merge.write(r_buffer1)
            r_buffer1 = file1.readline()

        while r_buffer2:
            merge.write(r_buffer2)
            r_buffer2 = file2.readline()
    return


# Take 2 indexes file at a time to merger them into a single file
merge_index("index_1.txt", "index_2.txt")
merge_index("merged_index.txt", "index_3.txt")
