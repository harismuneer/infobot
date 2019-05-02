import math
import sys

import matplotlib.pyplot as plt


##################################################################
##################################################################

# function to calculate dcg

def calculate_dcg(query_id, ranks, p_num):
    doc_scores = sorted(ranks[query_id].items(), key=lambda kv: (kv[1][1], kv[0]))

    dcg = doc_scores[0][1][0]

    for k in range(1, p_num):
        relevance = doc_scores[k][1][0]
        position = doc_scores[k][1][1]

        dcg += relevance / math.log(position)

    return round(dcg, ndigits=2)


##################################################################
##################################################################

# function to read ranks from a file

def read_ranks(ranks_file, is_baseline, base_ranks=None):
    ranks = dict()

    ranks_file = open(ranks_file)

    results = ranks_file.readlines()

    i = 1
    for r in results:
        r = r.rstrip().split()

        query_id = r[0]
        doc_name = r[2]

        if query_id not in ranks:
            ranks[query_id] = dict()
            i = 1

        # for IDCG
        if is_baseline == True:
            relevance = int(r[3])
            position = 0

        # for DCG
        else:
            if doc_name not in base_ranks[query_id]:
                relevance = 0
            else:
                relevance = base_ranks[query_id][doc_name][0]

            position = i

        ranks[query_id][doc_name] = [relevance, position]

        i += 1

    # for IDCG
    if is_baseline == True:
        for query_id in ranks.keys():
            # sort on basis of relevance
            doc_scores = sorted(ranks[query_id].items(), key=lambda kv: (kv[1][0], kv[0]), reverse=True)

            for j in range(len(doc_scores)):
                doc_name = doc_scores[j][0]

                ranks[query_id][doc_name][1] = j + 1


    ranks_file.close()

    return ranks


##################################################################
##################################################################


def main():
    corpus_file = sys.argv[1]
    run_file = sys.argv[2]
    p = int(sys.argv[3])
    # p = 300

    ##################################################################
    ##################################################################

    # load baseline document relevance scores and ranks
    baseline_ranks = read_ranks(corpus_file, True)

    # load our predicted documents and their ranks
    predicted_ranks = read_ranks(run_file, False, baseline_ranks)

    ##################################################################
    ##################################################################

    # compute Ideal Discounted Cumulative Gain (IDCG) using Baseline Ranks
    IDCG = dict()

    # compute Discounted Cumulative Gain (DCG) using Predicted Ranks
    DCG = dict()

    for query_id in baseline_ranks.keys():

        if p > len(baseline_ranks[query_id]) or p > len(predicted_ranks[query_id]):
            p_num = min(len(baseline_ranks[query_id]), len(predicted_ranks[query_id]))
        else:
            p_num = p

        idcg = calculate_dcg(query_id, baseline_ranks, p_num)
        dcg = calculate_dcg(query_id, predicted_ranks, p_num)

        IDCG[query_id] = idcg
        DCG[query_id] = dcg

    ##################################################################
    ##################################################################

    # compute Net Discounted Cumulative Gain (NDCG)
    NDCG = dict()

    print("----------------------------------------------------------")
    print("NDCG for Queries...")
    print("----------------------------------------------------------")

    sum = 0

    for query_id in DCG.keys():
        NDCG[query_id] = round(DCG[query_id] / IDCG[query_id], ndigits=2)

        sum += NDCG[query_id]

        print("Query:", query_id, "DCG:", DCG[query_id], "IDCG:", IDCG[query_id], "NDCG:", NDCG[query_id])

    avg_ndcg = round(sum / len(NDCG), ndigits=2)
    print("\n----------------------------------------------------------")
    print("Average NDCG:", avg_ndcg)
    print("----------------------------------------------------------")

    ##################################################################
    ##################################################################

    p_file = open("./p_file.txt", "a")
    p_file.write(str(p) + "," + str(avg_ndcg) + "\n")
    p_file.close()

    # p vs NDCG plot
    p_file = open("./p_file.txt")
    p_file = [t.rstrip() for t in p_file]

    x = []  # p values
    y = []  # ndcg values

    for t in p_file:
        r = t.split(",")
        x.append(r[0])
        y.append(r[1])

    fig = plt.figure()
    axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])  # left, bottom, width, height (range 0 to 1)
    axes.plot(x, y, 'r')

    axes.set_xlabel('p')
    axes.set_ylabel('NDCG')
    axes.set_title('p vs NDCG')
    fig.savefig("p vs NDCG.png")

##################################################################
##################################################################

if __name__ == '__main__':
    # get things rolling
    main()
