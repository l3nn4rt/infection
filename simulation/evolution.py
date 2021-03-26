import json

from infection.node import State

class Evolution:

    def __init__(self, graph):
        self.graph = graph
        self.rounds = []

    def update(self):
        self.rounds.append({
            'infectious': [l for l in self.graph.nodes \
                    if self.graph.nodes[l]['state'] == State.INFECTIOUS],
            'recovered': [l for l in self.graph.nodes \
                    if self.graph.nodes[l]['state'] == State.RECOVERED]
        })

    def __str__(self):
        return json.dumps({
            'nodes': list(self.graph.nodes),
            'rounds': self.rounds
        })
