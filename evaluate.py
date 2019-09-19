from collections import defaultdict
import editdistance
import networkx as nx
from networkx.algorithms.bipartite.matching import minimum_weight_full_matching

class Evaluator:
    def __init__(self):
        self.words = defaultdict(dict)

    def load(self, path):
        """
        :param path: path to the golden reference file
        """
        self.words.clear()
        with open(path) as f:
            for line in f:
                lemma, word, tag = line.split('\t')
                self.words[tag][lemma] = word
    
    def evaluate(self, prediction, distance_function=editdistance.eval):
        """
        :param prediction: Dict of dict in the form of {tag: {lemma: word}}.
        :param distance_function: Function that takes two strings and computes their distance.
                                  Default is edit distance.
        """
        graph = nx.Graph()
        src_nodes = ['src_' + tag for tag in prediction.keys()]
        tgt_nodes = ['tgt_' + tag for tag in self.words.keys()]
        graph.add_nodes_from(src_nodes)
        graph.add_nodes_from(tgt_nodes)

        for src_tag in prediction.keys():
            for tgt_tag in self.words.keys():
                total_distance = 0
                for lemma, src_word in prediction[src_tag].items():
                    tgt_word = self.words[tgt_tag].get(lemma, '')
                    total_distance += distance_function(src_word, tgt_word)
                graph.add_edge('src_' + src_tag, 'tgt_' + tgt_tag, weight=total_distance)
        
        num_words = sum(len(d) for d in prediction.values())
        matches = minimum_weight_full_matching(graph, src_nodes)
        match_distance = 0
        for src_node, tgt_node in matches.items():
            if src_node.startswith('src_'):
                match_distance += graph[src_node][tgt_node]['weight']
        return match_distance / num_words


if __name__ == '__main__':
    evaluator = Evaluator()
    evaluator.words['3sg.prs'] = {'get': 'gets', 'set': 'sets'}
    evaluator.words['pst'] = {'get': 'got', 'set': 'set'}
    prediction = {
        'one': {'get': 'get', 'set': 'set'},
        'two': {'get': 'getz', 'set': 'setz'}
    }
    assert evaluator.evaluate(prediction) == 0.75
