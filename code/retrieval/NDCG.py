import math
from sys import argv


# Function to compute NDCG at every position

def compute_score(corpus, results, p):

    # Initialization
    query_topics = []                               # contains ID'S of query
    total = []                                      # contains number of results obtained for every query(n in each case right now)
    query_results_p = []                            # contains first p results for every query
    relevance_score = []                            # contains relevance score for first p results
    discounted_cumulative_gain = []                 # contains dcg for positions till p for all queries
    norm_discounted_cumulative_gain = []            # contains ndcg for positions till p for all queries
    norm_dcg_at_p = []                              # contains ndcg for only position p for all queries

    # Extracting Topic Number for Queries and keeping track of how many results obtained for each Query(n = 3465 in this case)
    query_topics.append(results[0].split(" ")[0])
    total.append(1)
    for result in results:
        result = result.split(" ")
        if result[0] != query_topics[len(query_topics)-1]:
            query_topics.append(result[0])
            total.append(1)
        else:
            total[len(total)-1] += 1

    # Extracting p number of results for every Query
    for q in range(0, len(query_topics)):
        if q == 0:
            temp = results[:p]
        else:
            x = 0
            for t in range(0, q):
                x += total[t]
            temp = results[x-1:x+p-1]
        query_results_p.append(temp)

    # Now obtaining relevance score of the p documents for all Queries
    for q in range(0, len(query_results_p)):
        score = []
        for info in query_results_p[q]:
            info = info.split(" ")
            name = info[2]
            found = False
            for line in corpus:
                line = line.split(" ")
                if line[2] == name:
                    found = True
                    score.append(int(line[3].replace('\n','')))
            if not found:
                score.append(0)
        relevance_score.append(score)

    # Calculating DCG of the documents for all Queries
    for q in range(0, len(query_results_p)):
        gain = []
        score = relevance_score[q]
        gain.append(score[0])
        for i in range(1, len(score)):
            gain.append(float(score[i]) / (math.log(i+1, 2)))
        for j in range(1, len(gain)):
            gain[j] += gain[j-1]
        discounted_cumulative_gain.append(gain)

    # Calculating Normalized DCG of the documents for all Queries
    for q in range(0, len(query_results_p)):
        gain = []
        score = relevance_score[q]
        dcg = discounted_cumulative_gain[q]
        score = sorted(score, reverse=True)
        gain.append(score[0])
        for i in range(1, len(score)):
            gain.append(float(score[i]) / (math.log(i+1, 2)))
        for j in range(1, len(gain)):
            gain[j] += gain[j-1]
        for j in range(0, len(gain)):
            if int(gain[j]) is not 0:
                gain[j] = dcg[j]/gain[j]
        norm_discounted_cumulative_gain.append(gain)

    # Obtaining ndcg for position P for all queries
    for q in range(0, len(query_topics)):
        view = []
        view.append(query_topics[q])
        score = norm_discounted_cumulative_gain[q]
        view.append(score[p-1])
        norm_dcg_at_p.append(view)

    return norm_dcg_at_p

##################################################################
##################################################################


def main(corpus, run, constant, *args):

    file1 = open(run, "r")
    file2 = open(corpus, "r")
    c = file2.readlines()
    r = file1.readlines()
    values = compute_score(c, r, int(constant))


    mean = 0
    for value in values:
        print("NDCG for Query '"+str(value[0])+"'"+" is '"+str(round(value[1], ndigits=2))+"'")
        mean += value[1]

    avg = mean / len(values)
    print("Average of NDCG score for all queries is " +str(round(avg, ndigits=2)))
    return


if __name__ == '__main__':

    # get things rolling
    main(*argv[1:])
