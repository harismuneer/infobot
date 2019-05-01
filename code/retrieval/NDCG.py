import math
import sys


##################################################################
##################################################################


def main():
    corpus_file = sys.argv[1]
    run_file = sys.argv[2]
    p = int(sys.argv[3])

    ##################################################################
    ##################################################################

    # load baseline document relevance scores and ranks
    baseline_ranks = dict()

    corpus_file = open(corpus_file)

    results = corpus_file.readlines()

    i = 1
    for r in results:
        r = r.rstrip().split()

        query_id = r[0]
        doc_name = r[2]
        relevance = int(r[3])

        if query_id not in baseline_ranks:
            baseline_ranks[query_id] = dict()
            i = 1

        position = i
        baseline_ranks[query_id][doc_name] = (relevance,position)

        i += 1

    corpus_file.close()

    ##################################################################
    ##################################################################

    # load our predicted documents and their ranks
    predicted_ranks = dict()

    run_file = open(run_file)

    results = run_file.readlines()

    i = 1
    for r in results:
        r = r.rstrip().split()

        query_id = r[0]
        doc_name = r[2]

        if doc_name not in baseline_ranks[query_id]:
            relevance = 0
        else:
            relevance = baseline_ranks[query_id][doc_name][0]

        if query_id not in predicted_ranks:
            predicted_ranks[query_id] = dict()
            i = 1

        position = i
        predicted_ranks[query_id][doc_name] = (relevance, position)

        i += 1

    run_file.close()

    ##################################################################
    ##################################################################

    # compute Ideal Discounted Cumulative Gain (IDCG) using Baseline Ranks
    IDCG = dict()

    for query_id in baseline_ranks.keys():

        doc_scores = sorted(baseline_ranks[query_id].items(), key=lambda kv: (kv[1][1], kv[0]))

        idcg = doc_scores[0][1][0]

        if p > len(baseline_ranks[query_id]) or p > len(predicted_ranks[query_id]):
            p_num = min(len(baseline_ranks[query_id]), len(predicted_ranks[query_id]))
        else:
            p_num = p

        for k in range(1, p_num):
            relevance = doc_scores[k][1][0]
            position = doc_scores[k][1][1]

            idcg += relevance/math.log(position)

        IDCG[query_id] = round(idcg, ndigits=2)

    ##################################################################
    ##################################################################

    # compute Discounted Cumulative Gain (DCG) using Predicted Ranks
    DCG = dict()

    for query_id in predicted_ranks.keys():

        doc_scores = sorted(predicted_ranks[query_id].items(), key=lambda kv: (kv[1][1], kv[0]))

        dcg = doc_scores[0][1][0]

        if p > len(baseline_ranks[query_id]) or p > len(predicted_ranks[query_id]):
            p_num = min(len(baseline_ranks[query_id]), len(predicted_ranks[query_id]))
        else:
            p_num = p

        for k in range(1, p_num):
            relevance = doc_scores[k][1][0]
            position = doc_scores[k][1][1]

            dcg += relevance / math.log(position)

        DCG[query_id] = round(dcg, ndigits=2)

    ##################################################################
    ##################################################################

    # compute Net Discounted Cumulative Gain (NDCG)
    NDCG = dict()

    print("----------------------------------------------------------")
    print("NDCG for Queries...")
    print("----------------------------------------------------------")

    sum = 0

    for query_id in DCG.keys():
        NDCG[query_id] = round(DCG[query_id]/IDCG[query_id], ndigits=2)

        sum += NDCG[query_id]

        print("Query Number:", query_id, "DCG:", DCG[query_id], "IDCG:", IDCG[query_id], "NDCG:" ,NDCG[query_id])

    print("\n----------------------------------------------------------")
    print("Average NDCG:", round(sum/len(NDCG), ndigits=2))
    print("----------------------------------------------------------")

    ##################################################################
    ##################################################################


if __name__ == '__main__':

    # get things rolling
    main()
