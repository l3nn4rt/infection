import json
import math

from infection.node import NodeState

class Evolution:
    def __init__(self, graph):
        self.graph = graph
        self.rounds = []

    def update(self):
        self.rounds.append({
            'infectious': [l for l in self.graph.nodes \
                    if self.graph.nodes[l]['state'] == NodeState.INFECTIOUS],
            'recovered': [l for l in self.graph.nodes \
                    if self.graph.nodes[l]['state'] == NodeState.RECOVERED]
        })

    def __str__(self):
        return json.dumps({
            'nodes': list(self.graph.nodes),
            'rounds': self.rounds
        })

    @property
    def json(self):
        return json.dumps({
            'nodes': list(self.graph.nodes),
            'rounds': self.rounds
        })

    @property
    def timeline(self):
        lines = []
        prefix_width = math.ceil(math.log10(len(self.rounds) + 1))
        for round_idx, round_dict in enumerate(self.rounds):
            line_lst = ['[%*d] ' % (prefix_width, round_idx)]
            for label in sorted(self.graph, key=str):
                if label in round_dict['infectious']:
                    line_lst.append(NodeState.INFECTIOUS.value['cli_str'])
                elif label in round_dict['recovered']:
                    line_lst.append(NodeState.RECOVERED.value['cli_str'])
                else:
                    line_lst.append(NodeState.SUSCEPTIBLE.value['cli_str'])
            lines.append(''.join(line_lst))
        return '\n'.join(lines)
