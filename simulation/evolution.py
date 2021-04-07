import random

class Evolution:

    def __init__(self, graph, zeroes, contagion_probability:float,
            infection_duration:int=1, recovery_duration:int=None):
        """
        Random infection evolution.

        Parameters:
            * graph (networkx.Graph): network to use for infection spreading
            * zeroes (iterable): initially infectious graph nodes
            * contagion_probability (float): probability an infectious node
              has to infect a susceptible neighbor on each round
            * infection_duration (int): how many rounds a node is infectious
              after being infected (starting from the next round)
            * recovery_duration (int|None): how many rounds a recovered node
              is immune; if None, a recovered node will not become
              susceptible again

        Attributes:
            * rounds (list): list of rounds; each round is a dictionary with
              two keys:
                - 'i': list of infectious nodes
                - 'r': list of recovered nodes
        """
        self.rounds = []

        # init node states
        self.__susceptible = set(graph).difference(zeroes)
        self.__infectious = set(zeroes)
        self.__recovered = set()
        # round when the current state ends
        self.__state_end = dict.fromkeys(zeroes, infection_duration)

        # save initial round
        self._save_round_states()

        # - the infection spreading consists of a sequence of rounds;
        # - each round consists of two phases:
        #   1. infection
        #   2. update
        while self.__infectious:
            # 1. infectious nodes try to infect susceptible neighbors
            round_n = len(self.rounds)
            infected = set()
            for i in self.__infectious:
                for neigh in graph.neighbors(i):
                    if neigh in self.__susceptible \
                            and random.random() < contagion_probability:
                        infected.add(neigh)

            # 2. node states are updated for the next round
            for node in graph.nodes:
                # susceptible node becomes infected
                if node in self.__susceptible and node in infected:
                    self.__susceptible.remove(node)
                    self.__infectious.add(node)
                    self.__state_end[node] = round_n + infection_duration
                # infectious node becomes recovered
                elif node in self.__infectious \
                        and self.__state_end[node] == round_n:
                    self.__infectious.remove(node)
                    self.__recovered.add(node)
                    if recovery_duration:
                        self.__state_end[node] = round_n + recovery_duration
                # recovered node becomes susceptible
                elif node in self.__recovered and recovery_duration \
                        and self.__state_end[node] == round_n:
                    self.__susceptible.add(node)
                    self.__state_end.pop(node)

            # save current round
            self._save_round_states()

    def _save_round_states(self):
        self.rounds.append({
            'i': [*self.__infectious],
            'r': [*self.__recovered]
        })
