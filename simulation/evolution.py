import json

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
