import random

class Evolution:

    def __init__(self, graph, zeroes, contagion_probability,
                 infection_duration=1, recovery_duration=None):
        self.__graph = graph
        self.__contagion_probability = contagion_probability
        self.__infection_duration = infection_duration
        self.__recovery_duration = recovery_duration
        self.__rounds = []
        # init node states
        self.__susceptible = set(graph).difference(zeroes)
        self.__infectious = set(zeroes)
        self.__recovered = set()
        # round when the current state ends
        self.__state_end = dict.fromkeys(zeroes, infection_duration)

        self._save_round_states()

    @property
    def rounds(self):
        """
        List of infection rounds. It contains the initial state only until
        `Evolution.run()` is executed.
        """
        return self.__rounds

    def run(self):
        """Spread infection over self.__graph."""
        # - the infection spreading consists of a sequence of rounds;
        # - each round consists of two phases:
        #   1. infection
        #   2. update
        while self.__infectious:
            # 1. infectious nodes try to infect susceptible neighbors
            round_n = len(self.__rounds)
            infected = set()
            for i in self.__infectious:
                for neigh in self.__graph.neighbors(i):
                    if neigh in self.__susceptible \
                            and random.random() < self.__contagion_probability:
                        infected.add(neigh)

            # 2. node states are updated for the next round
            for node in self.__graph.nodes:
                # susceptible node becomes infected
                if node in self.__susceptible and node in infected:
                    self.__susceptible.remove(node)
                    self.__infectious.add(node)
                    self.__state_end[node] = round_n + self.__infection_duration
                # infectious node becomes recovered
                elif node in self.__infectious \
                        and self.__state_end[node] == round_n:
                    self.__infectious.remove(node)
                    self.__recovered.add(node)
                    if self.__recovery_duration:
                        self.__state_end[node] = round_n + self.__recovery_duration
                # recovered node becomes susceptible
                elif node in self.__recovered and self.__recovery_duration \
                        and self.__state_end[node] == round_n:
                    self.__susceptible.add(node)
                    self.__state_end.pop(node)

            self._save_round_states()

    def _save_round_states(self):
        self.__rounds.append({
            'i': [*self.__infectious],
            'r': [*self.__recovered]
        })
