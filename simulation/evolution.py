import json

from infection.node import NodeState

class InfectionEvolution:
    def __init__(self, graph):
        self.g = graph
        self.rounds = []

    def update(self):
        self.rounds.append({
            'infectious': [l for l in self.g.nodes \
                    if self.g.nodes[l]['state'] == NodeState.INFECTIOUS],
            'recovered': [l for l in self.g.nodes \
                    if self.g.nodes[l]['state'] == NodeState.RECOVERED]
        })

    def __str__(self):
        return json.dumps({
            'nodes': list(self.g.nodes),
            'rounds': self.rounds
        })


