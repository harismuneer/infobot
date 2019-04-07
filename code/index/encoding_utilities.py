from __future__ import division

from struct import pack, unpack


##################################################################
##################################################################

# takes a single number and encodes it using variable byte encoding
def encode_number(number):
    bytes_list = []

    while True:
        bytes_list.insert(0, number % 128)
        if number < 128:
            break
        number = number // 128

    bytes_list[-1] += 128

    return pack('%dB' % len(bytes_list), *bytes_list)

##################################################################
##################################################################

# takes a list of numbers and encodes it using variable byte encoding
def encode(numbers):
    bytes_list = []

    for number in numbers:
        bytes_list.append(encode_number(number))

    return b"".join(bytes_list)

##################################################################
##################################################################

# takes a byte stream and decodes it
def decode(bytestream):
    n = 0
    numbers = []
    bytestream = unpack('%dB' % len(bytestream), bytestream)

    for byte in bytestream:
        if byte < 128:
            n = 128 * n + byte
        else:
            n = 128 * n + (byte - 128)
            numbers.append(n)
            n = 0

    return numbers

##################################################################
##################################################################

# takes a posting list and encodes it
def compress_posting_list(posting_list):
    doc_freq = posting_list[0]
    posting_list = posting_list[1]

    d_encoded_posting_list = list()
    d_encoded_posting_list.append(doc_freq)

    document_ids = sorted(posting_list.keys())

    for k in range(len(document_ids)):

        # delta encode document_ids
        if k == 0:
            # place first d_id along-with t_freq
            d_encoded_posting_list.append(document_ids[0])
            d_encoded_posting_list.append(posting_list[document_ids[0]][0])

        else:
            delta = document_ids[k] - document_ids[k - 1]
            t_freq = posting_list[document_ids[k]][0]

            d_encoded_posting_list.append(delta)
            d_encoded_posting_list.append(t_freq)

        # delta encode term_positions
        t_positions = posting_list[document_ids[k]][1]

        for l in range(len(t_positions)):
            if l == 0:
                # place first t_position as it is
                d_encoded_posting_list.append(t_positions[0])

            else:
                d_encoded_posting_list.append(t_positions[l] - t_positions[l - 1])

    # do variable byte encoding of the delta encoded posting list
    return encode(d_encoded_posting_list)

##################################################################
##################################################################

# make original posting list from the compressed one
def decompress_posting_list(encoded_posting_list):

    # decode variable byte encoded list to delta encoded list
    d_encoded_posting_list = decode(encoded_posting_list)

    # decode delta encoded gap list to original posting list
    doc_freq = d_encoded_posting_list[0]

    k = 1

    original_posting_list = list()
    original_posting_list.append(doc_freq)
    original_posting_list.append(dict())

    d_id = 0

    # extract gap encoded document ids
    for i in range(doc_freq):

        d_id += d_encoded_posting_list[k]
        k += 1

        original_posting_list[1][d_id] = list()

        # append term frequency
        term_freq = d_encoded_posting_list[k]
        original_posting_list[1][d_id].append(term_freq)
        k += 1

        original_posting_list[1][d_id].append(list())

        t_pos = 0

        # extract gap encoded term positions
        for j in range(term_freq):
            t_pos += d_encoded_posting_list[k]
            original_posting_list[1][d_id][1].append(t_pos)
            k += 1

    return original_posting_list


##################################################################
##################################################################

# take a comma separated posting list string and converts it into a dictionary
def make_posting_dic(p_list):
    p_list = [int(i) for i in p_list]

    doc_freq = p_list[0]

    k = 1

    original_posting_list = list()
    original_posting_list.append(doc_freq)
    original_posting_list.append(dict())

    for i in range(doc_freq):

        d_id = p_list[k]
        k += 1

        original_posting_list[1][d_id] = list()

        # append term frequency
        term_freq = p_list[k]
        original_posting_list[1][d_id].append(term_freq)
        k += 1

        original_posting_list[1][d_id].append(list())

        for j in range(term_freq):
            t_pos = p_list[k]
            original_posting_list[1][d_id][1].append(t_pos)
            k += 1

    return original_posting_list

##################################################################
##################################################################