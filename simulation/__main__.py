#!/usr/bin/env python3
# vim: ts=8 et sw=4 sts=4
"""
Simulate epidemic spreading in a SI[R][S]-model based network.
"""

import argparse
import enum
import json
import random

import networkx as nx
#import matplotlib.pyplot as plt

import plot_basic


class NodeState(enum.Enum):
    SUSCEPTIBLE = {
            'cli_str': '\033[1;34m*\033[0m',
            'plt_col': 'lightblue'
    }
    INFECTIOUS  = {
            'cli_str': '\033[1;31m*\033[0m',
            'plt_col': 'red'
    }
    RECOVERED   = {
            'cli_str': '\033[1;32m*\033[0m',
            'plt_col': 'green'
    }


class Animation:
    def __init__(self, graph):
        self.g = graph

    def update(self):
        cols = [self.g.nodes[l]['state'].value['plt_col'] for l in self.g.nodes]
        #nx.draw(self.g, pos=nx.spring_layout(self.g),
        #        with_labels=True, node_color=cols)
        #plt.show()
        plot_basic.plot_graph(self.g, cols)


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


def print_timeline(t, g):
    print('[%3d]' % t, ''.join([g.nodes[l]['state'].value['cli_str']
        for l in sorted(g, key=str)]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    # input graph file
    parser.add_argument('graph_file', metavar='GRAPH-FILE',
            help="""File containing the graph adjacency list or the graph edge
            list without data. If missing or -, read standard input.""",
            type=argparse.FileType(), nargs='?', default='-')
    # plot animation (default: false)
    parser.add_argument('-a', '--animate',
            help="""Animate the contagion; this is very CPU-intensive and not
            suitable for large graphs.""", action='store_true')
    # flag to read graph file as edge list (default: false)
    parser.add_argument('-e', '--edges',
            help="""Treat graph file as edge list. This option allows to ignore
            edge datas, but requires the edges to be written one per line.""",
            action='store_true')
    # infectiousness duration
    parser.add_argument('-i', '--infection', metavar='ROUNDS',
            help="""How many rounds can an infectious node spread the infection.
            If missing, the infection duration is one round (i.e. the node
            becomes recovered after one round in the infectious state).""",
            type=int, default=1)
    # print infection evolution (default: false)
    parser.add_argument('-j', '--json',
            help="""Print infection evolution on the standard output in JSON.
            Property 'nodes' contains the list of graph nodes. Property 'rounds'
            contains a list of objects for the infection rounds; each
            round contains properties 'infectious' and 'recovered';
            'infectious' property contains the list of infectious nodes at the
            given round; 'recovered' property contains the list of recovered
            nodes at the given round.""", action='store_true')
    # try to save nodes as integers
    parser.add_argument('-n', '--numeric', metavar='MODE',
            help="""Treat node labels as numbers when possible. If MODE is
            'auto', perform conversion if all nodes can be treated as numbers,
            otherwise all labels will be treated as strings ("all-or-none").
            If MODE is 'always', perform conversion on any label for which it is
            possible, and treat as strings all the others. If MODE is missing,
            default is 'auto'.""", choices=['always', 'auto'], nargs='?',
            const='auto')
    # infection probability
    parser.add_argument('-p', '--probability', metavar='VALUE',
            help="""Probability a node has to infect nearby nodes on each round.
            This values must be in [0,1].""", type=float, required=True)
    # immunization duration
    parser.add_argument('-r', '--recovery', metavar='ROUNDS',
            help="""How many rounds a recovered node is immune to the infection.
            If missing, the recovered state is final (i.e. the node will not
            become susceptible again).""", type=int, default=None)
    # print timeline (default: false)
    parser.add_argument('-t', '--timeline',
            help="""Print node states at each round on the standard output; this
            option requires a color-capable terminal.""", action='store_true')
    # initially infectious nodes(s):
    zero_g = parser.add_mutually_exclusive_group(required=True)
    # - from the command line
    zero_g.add_argument('-z', '--zero', metavar='LIST',
            help="""Comma separated initially infectious nodes. Nodes not in the
            graph will be ignored.""", type=str)
    # - from a file
    zero_g.add_argument('-Z', '--zero-file', metavar='ZERO-FILE',
            help="""File containing the initially infectious nodes (one node per
            line; comments start with #).""", type=argparse.FileType())
    # parse sys.argv
    args = parser.parse_args()

    # check args ranges
    assert args.infection >= 1, \
            "infection: ROUNDS must be a positive integer"
    assert 0 <= args.probability <= 1, \
            "probability: PROBABILITY must be in [0,1]"
    assert args.recovery == None or args.recovery >= 1, \
            "recovery: ROUNDS must be a positive integer"

    # generate graph
    if args.edges:
        g = nx.parse_edgelist(args.graph_file)
    else:
        g = nx.parse_adjlist(args.graph_file)

    # read infectious nodes
    if args.zero:
        zeroes = set(x for x in args.zero.split(',') if x in g)
    else:
        lines = [l.split('#')[0].strip() for l in args.zero_file]
        zeroes = set(l for l in lines if l in g)

    # numeric conversion
    if args.numeric:
        # store valid substitutions only
        subs = {}
        for label in g.nodes:
            try:
                subs[label] = int(label)
            except ValueError as _:
                if args.numeric == 'auto':
                    # abort if any conversion fails
                    break
        else:
            g = nx.relabel_nodes(g, subs)
            zeroes.update({subs[label] for label in subs if label in zeroes})
            zeroes.difference_update(subs)

    # init node states
    infectious = set()
    for label in g.nodes:
        node = g.nodes[label]
        if label in zeroes:
            node['state'] = NodeState.INFECTIOUS
            # round when the current state ends
            node['state-end'] = args.infection - 1
            infectious.add(label)
        else:
            node['state'] = NodeState.SUSCEPTIBLE

    curr_round = 0
    if args.timeline:
        print_timeline(curr_round, g)
    animation = None
    if args.animate:
        animation = Animation(g)
        animation.update()
    evolution = None
    if args.json:
        evolution = InfectionEvolution(g)
        evolution.update()

    # - the infection spreading consists of a sequence of rounds;
    # - each round consists of two phases:
    #   1. infection
    #   2. update
    while infectious:
        # 1. infectious nodes try to infect susceptible neighbors
        infected = set()
        for i in infectious:
            for neigh in g.neighbors(i):
                if g.nodes[neigh]['state'] == NodeState.SUSCEPTIBLE \
                        and random.random() < args.probability:
                    infected.add(neigh)

        # 2. node states are updated for the next round
        for label in g.nodes:
            node = g.nodes[label]
            # susceptible node becomes infected
            if node['state'] == NodeState.SUSCEPTIBLE \
                    and label in infected:
                node['state'] = NodeState.INFECTIOUS
                node['state-end'] = curr_round + args.infection
                infectious.add(label)
            # infectious node becomes recovered
            elif node['state'] == NodeState.INFECTIOUS \
                    and node['state-end'] == curr_round:
                node['state'] = NodeState.RECOVERED
                if args.recovery:
                    node['state-end'] = curr_round + args.recovery
                infectious.remove(label)
            # recovered node becomes susceptible
            elif node['state'] == NodeState.RECOVERED \
                    and node['state-end'] == curr_round \
                    and args.recovery is not None:
                node['state'] = NodeState.SUSCEPTIBLE
                node['state-end'] = None

        curr_round += 1
        if args.timeline:
            print_timeline(curr_round, g)
        if args.animate:
            animation.update()
        if args.json:
            evolution.update()

    if args.json:
        print(evolution)

if __name__ == "__main__":
    main()
