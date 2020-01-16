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
    with open(path, encoding='utf8') as f:
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
    with open(path, encoding='utf8') as f:
        for line in f:
            lemma, word, tag = line.split('\t')
            d[tag][lemma] = word
    return d


class Evaluator:
    def __init__(self, reference):
        """
        :param reference: The golden reference. Dict of dict of set like {tag: {lemma: {word}}}.
        """
        self._check_dict_dict(reference, lambda s: isinstance(s, set) and len(s) > 0, 'reference')
        self.reference = reference

    def _check_dict_dict(self, dd, check_value=None, arg_name=''):
        if not isinstance(dd, dict) or not all(isinstance(key, str) for key in dd.keys()) \
                or not all(isinstance(value, dict) for value in dd.values()) \
                or not all(isinstance(key, str) for d in dd.values() for key in d):
            raise ValueError("'{}' is not of type dict[str, dict[str, _]]".format(arg_name))
        if check_value is not None:
            for d in dd.values():
                for value in d.values():
                    if not check_value(value):
                        raise ValueError("'{}' has an invalid value: {}".format(arg_name, value))

    def _get_metric(self, true_pos, prd_size, ref_size, metric):
        precision = true_pos / prd_size if prd_size > 0 else 0
        recall = true_pos / ref_size if ref_size > 0 else 0
        if metric == 'precision':
            return precision
        elif metric == 'recall':
            return recall
        elif metric == 'f1':
            return precision * recall * 2 / (precision + recall) if precision + recall > 0 else 0

    def score(self, prediction, metric='f1', average='macro'):
        """
        :param prediction: The prediction of your model. Dict of dict like {tag: {lemma: word}}.
        :param metric: Metric for calculating per-slot-pair score.
        :param average: Type of average.
        :returns: The overall score.
        """
        self._check_dict_dict(prediction, lambda s: isinstance(s, str), 'prediction')
        if metric not in ['f1', 'precision', 'recall']:
            raise ValueError("'metric' must be 'precision', 'recall' or 'f1', got '{}'.".format(metric))
        if average not in ['micro', 'macro']:
            raise ValueError("'average' must be 'micro' or 'macro', got '{}'.".format(average))
        
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
                if average == 'micro':
                    tag_score = true_pos
                else:
                    tag_score = self._get_metric(true_pos, len(prd_dict), len(ref_dict), metric)
                graph.add_edge('prd_' + prd_tag, 'ref_' + ref_tag, weight=-tag_score)

        matches = minimum_weight_full_matching(graph, prd_nodes)
        match_score = 0
        for prd_node, ref_node in matches.items():
            if prd_node in prd_nodes:
                match_score -= graph[prd_node][ref_node]['weight']
        if average == 'micro':
            total_prd = sum(len(prd_dict) for prd_dict in prediction.values())
            total_ref = sum(len(ref_dict) for ref_dict in reference.values())
            final_score = self._get_metric(match_score, total_prd, total_ref, metric)
            return final_score * len(self.reference) / max(len(self.reference), len(prediction))
        else:
            return match_score / max(len(self.reference), len(prediction))


if __name__ == '__main__':
    parser = ArgumentParser(description='Evaluate morphology paradigm prediction.')
    parser.add_argument('reference', help='The ground truth file')
    parser.add_argument('prediction', help='The prediction file')
    parser.add_argument('--metric', default='recall', help='The metric to report')
    parser.add_argument('--average', default='macro', choices=['micro', 'macro'], help='Type of averaging.')
    args = parser.parse_args()
    
    reference = load_reference(args.reference)
    prediction = load_prediction(args.prediction)
    evaluator = Evaluator(reference)
    print("{} predicted slots".format(len(prediction)))
    print("macro: {}".format(evaluator.score(prediction, args.metric, 'macro')))
    print("micro: {}".format(evaluator.score(prediction, args.metric, 'micro')))
