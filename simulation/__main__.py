#!/usr/bin/env python3
# vim: ts=8 et sw=4 sts=4
"""
Simulate epidemic spreading in a SI[R][S]-model based network.
"""

import argparse

import networkx as nx

from infection.simulation.evolution import Evolution


def main():
    parser = argparse.ArgumentParser(prog=__package__, description=__doc__)
    # input graph file
    parser.add_argument('graph_file', metavar='GRAPH-FILE',
            help="""File containing the graph adjacency list or the graph edge
            list without data. If missing or -, read standard input.""",
            type=argparse.FileType(), nargs='?', default='-')
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

    evolution = Evolution(g, zeroes, args.probability,
                          args.infection, args.recovery)
    evolution.run()
    print(evolution)

if __name__ == "__main__":
    main()
