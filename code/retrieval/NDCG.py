import math
import sys


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

        if is_baseline == True:
            relevance = int(r[3])
        else:
            if doc_name not in base_ranks[query_id]:
                relevance = 0
            else:
                relevance = base_ranks[query_id][doc_name][0]

        if query_id not in ranks:
            ranks[query_id] = dict()
            i = 1

        position = i
        ranks[query_id][doc_name] = (relevance, position)

        i += 1

    ranks_file.close()

    return ranks


##################################################################
##################################################################


def main():
    corpus_file = sys.argv[1]
    run_file = sys.argv[2]
    p = int(sys.argv[3])

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

    print("\n----------------------------------------------------------")
    print("Average NDCG:", round(sum / len(NDCG), ndigits=2))
    print("----------------------------------------------------------")

    ##################################################################
    ##################################################################


if __name__ == '__main__':
    # get things rolling
    main()
