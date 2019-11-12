from collections import defaultdict
import networkx as nx
from networkx.algorithms.bipartite.matching import minimum_weight_full_matching
from argparse import ArgumentParser


def load_reference(path):
    """
    :param path: path to the golden reference file
    :returns: Dict of dict of set like {tag: {lemma: {word}}}.
    """
    d = defaultdict(lambda: defaultdict(set))
    with open(path) as f:
        for line in f:
            lemma, word, tag = line.split('\t')
            d[tag][lemma].add(word)
    return d


def load_prediction(path):
    """
    :param path: path to the prediction file
    :returns: Dict of dict like {tag: {lemma: word}}.
    """
    d = defaultdict(dict)
    with open(path) as f:
        for line in f:
            lemma, word, tag = line.split('\t')
            d[tag][lemma] = word
    return d


class Evaluator:
    def __init__(self, reference):
        """
        :param reference: The golden reference. Dict of dict of set like {tag: {lemma: {word}}}.
        """
        self.reference = reference

    def score(self, prediction, metric='f1'):
        """
        :param prediction: The prediction of your model. Dict of dict like {tag: {lemma: word}}.
        :param metric: Metric for calculating per-slot-pair score.
        :returns: The overall score.
        """
        graph = nx.Graph()
        prd_nodes = frozenset('prd_' + tag for tag in prediction.keys())
        ref_nodes = frozenset('ref_' + tag for tag in self.reference.keys())
        graph.add_nodes_from(prd_nodes)
        graph.add_nodes_from(ref_nodes)

        for prd_tag, prd_dict in prediction.items():
            for ref_tag, ref_dict in self.reference.items():
                true_pos = 0
                for lemma, prd_word in prd_dict.items():
                    ref_set = ref_dict.get(lemma)
                    if ref_set is not None and prd_word in ref_set:
                        true_pos += 1
                precision = true_pos / len(prd_dict) if len(prd_dict) > 0 else 0
                recall = true_pos / len(ref_dict) if len(ref_dict) > 0 else 0
                if metric == 'precision':
                    tag_score = precision
                elif metric == 'recall':
                    tag_score = recall
                elif metric == 'f1':
                    tag_score = precision * recall * 2 / (precision + recall) if precision + recall > 0 else 0
                else:
                    raise ValueError("'measure' must be 'precision', 'recall' or 'f1', got '%s'." % measure)
                graph.add_edge('prd_' + prd_tag, 'ref_' + ref_tag, weight=-tag_score)

        matches = minimum_weight_full_matching(graph, prd_nodes)
        match_score = 0
        for prd_node, ref_node in matches.items():
            if prd_node in prd_nodes:
                match_score -= graph[prd_node][ref_node]['weight']
        return match_score / max(len(self.reference), len(prediction))


if __name__ == '__main__':
    parser = ArgumentParser(description='Evaluate morphology paradigm prediction.')
    parser.add_argument('reference', help='The ground truth file')
    parser.add_argument('prediction', help='The prediction file')
    parser.add_argument('--metric', default='recall', help='The metric to report')
    args = parser.parse_args()
    
    reference = load_reference(args.reference)
    prediction = load_prediction(args.prediction)
    evaluator = Evaluator(reference)
    print(evaluator.score(prediction, args.metric))
