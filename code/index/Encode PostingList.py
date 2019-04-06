def append_zeros(num):
    length = len(num)
    count = 7 - length
    zero = ''
    for i in range(0, count):
        zero = zero + '0'
    return zero


def encode_number(num):
    binary = f'{num:00b}'
    binary = str(binary)
    mod = len(binary) % 7
    MSByte = append_zeros(binary[0:mod]) + binary[0:mod]
    binary = binary.replace(binary[0:mod], '',1)
    if len(binary) is 0:
        MSByte = '1' + MSByte
        return hex(int(MSByte, 2))
    else:
        remainBytes = []
        while len(binary) is not 0:
            remainBytes.append(binary[0:7])
            binary = binary.replace(binary[0:7], '', 1)
        MSByte = '0' + MSByte
        for i in range(0, len(remainBytes)):
            if i == len(remainBytes)-1:
                remainBytes[i] = '1' + remainBytes[i]
            else:
                remainBytes[i] = '0' + remainBytes[i]

        result = MSByte
        for byte in remainBytes:
            result = result + byte
        return hex(int(result, 2))


def encode_list(index):

    path = index
    with open(path, 'r') as file:
        holder1 = file.read()

    index = index[0:7]
    path = index+"_posting.txt"
    post = open(path, "w+", encoding='latin-1', errors='ignore')
    para = holder1.split("\n")


    # BHT ROUGH TAREEQAY SEA GAPS CALCULATE KIYE HAIN FOR DOC AND POS
    '''i = 0
    while i < 1:
        info = para[i].split(",")
        info = info[0:len(info)-1]
        doc = []
        index = []
        gap = []
        doc_freq = int(info[1])
        en_doc_freq = encode_number(doc_freq)
        j = 3
        index.append(2)
        doc.append(int(info[2]))
        gap.append(encode_number(int(info[2])))
        # print(info[0])
        while j < len(info):
            j = j + int(info[j])+1
            if j < len(info):
                if info[j] is not '':
                    index.append(j)
                    doc.append(int(info[j]))
                j += 1
        print(doc)
        for k in range(0, len(doc)-1):
            gap.append(encode_number(doc[k+1]-doc[k]))

        for k in range(0, len(doc)-1):
            doc[k] = encode_number(doc[k])
        p_index = []
        freq = []
        for k in range(0, len(index)-1):
            c = index[k] + 1+1
            freq.append(encode_number(int(info[index[k] + 1])))
            temp = []
            while c is not index[k+1]:
                temp.append(c)
                c += 1
            p_index.append(temp)
        c = index[len(index)-1]+1+1
        freq.append(encode_number(int(info[index[len(index)-1] + 1])))
        temp = []
        while c < len(info):
             temp.append(c)
             c += 1
        p_index.append(temp)
        pos_gap = []
        for po in p_index:
            temp = []
            temp.append(encode_number(int(info[po[0]])))
            for k in range(0, len(po)-1):
                temp.append(encode_number(int(info[po[k+1]]) - int(info[po[k]])))
            pos_gap.append(temp)
        for k in range(0, len(doc)):
            post.write(gap[k]+",")
            post.write(freq[k]+",")
            for item in pos_gap:
                post.write("%s\n" % item)
                post.write(",")

        i += 1

    return'''


encode_list("index_1.txt")
