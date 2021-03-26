import json
import random

from infection.node import State

class Evolution:

    def __init__(self, graph, zeroes, contagion_probability,
                 infection_duration=1, recovery_duration=None):
        self.graph = graph
        self.zeroes = zeroes
        self.contagion_probability = contagion_probability
        self.infection_duration = infection_duration
        self.recovery_duration = recovery_duration
        self.rounds = []
        self.infectious = set()

        # init node states
        for label in self.graph.nodes:
            node = self.graph.nodes[label]
            if label in self.zeroes:
                node['state'] = State.INFECTIOUS
                # round when the current state ends
                node['state-end'] = self.infection_duration
                self.infectious.add(label)
            else:
                node['state'] = State.SUSCEPTIBLE

        self._save_round_states()

    @property
    def round_count(self):
        """
        How many rounds the infection lasted.
        This is always greater or equal to one (even if zeroes is empty).
        """
        return len(self.rounds)

    def run(self):
        """Spread infection over self.graph."""
        # - the infection spreading consists of a sequence of rounds;
        # - each round consists of two phases:
        #   1. infection
        #   2. update
        while self.infectious:
            # 1. infectious nodes try to infect susceptible neighbors
            infected = set()
            for i in self.infectious:
                for neigh in self.graph.neighbors(i):
                    if self.graph.nodes[neigh]['state'] == State.SUSCEPTIBLE \
                            and random.random() < self.contagion_probability:
                        infected.add(neigh)

            # 2. node states are updated for the next round
            for label in self.graph.nodes:
                node = self.graph.nodes[label]
                # susceptible node becomes infected
                if node['state'] == State.SUSCEPTIBLE \
                        and label in infected:
                    node['state'] = State.INFECTIOUS
                    node['state-end'] = self.round_count + self.infection_duration
                    self.infectious.add(label)
                # infectious node becomes recovered
                elif node['state'] == State.INFECTIOUS \
                        and node['state-end'] == self.round_count:
                    node['state'] = State.RECOVERED
                    if self.recovery_duration:
                        node['state-end'] = self.round_count + self.recovery_duration
                    self.infectious.remove(label)
                # recovered node becomes susceptible
                elif node['state'] == State.RECOVERED \
                        and node['state-end'] == self.round_count \
                        and self.recovery_duration is not None:
                    node['state'] = State.SUSCEPTIBLE
                    node['state-end'] = None

            self._save_round_states()

    def _save_round_states(self):
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
