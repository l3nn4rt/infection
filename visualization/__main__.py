#!/usr/bin/env python3
# vim: ts=8 et sw=4 sts=4
"""
Visualize epidemic spreading in a SI[R][S]-model based network.
"""

import argparse
import json

import networkx as nx

from infection.visualization.animation import Animation2D
from infection.visualization.timeline import Timeline


def main():
    parser = argparse.ArgumentParser(prog=__package__, description=__doc__)
    # input graph file
    parser.add_argument('evolution_file', metavar='EVOLUTION',
            help="""File containing the infection evolution (JSON format).
            If missing or -, read standard input.""",
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
    # try to save nodes as integers
    parser.add_argument('-n', '--numeric', metavar='MODE',
            help="""Treat node labels as numbers when possible. If MODE is
            'auto', perform conversion if all nodes can be treated as numbers,
            otherwise all labels will be treated as strings ("all-or-none").
            If MODE is 'always', perform conversion on any label for which it is
            possible, and treat as strings all the others. If MODE is missing,
            default is 'auto'.""", choices=['always', 'auto'], nargs='?',
            const='auto')
    # print timeline (default: false)
    parser.add_argument('-t', '--timeline',
            help="""Print node states at each round on the standard output; this
            option requires a color-capable terminal.""", action='store_true')
    # - from a file
    parser.add_argument('-g', '--graph-file', metavar='GRAPH-FILE',
            help="""File containing the graph adjacency list or the graph edge
            list without data. This option takes precedence over any graph path
            or adjacency/edge list found in the EVOLUTION file.""",
            type=argparse.FileType(), nargs='?')
    # parse sys.argv
    args = parser.parse_args()

    evo = json.load(args.evolution_file)

    # scan graph description sources in decreasing priority
    if args.graph_file:
        graph_descr = args.graph_file
    elif 'graph' in evo and 'abspath' in evo['graph']:
        with open(evo['graph']['abspath']) as f:
            graph_descr = f.readlines()
    elif 'graph' in evo and 'adjlist' in evo['graph']:
        graph_descr = evo['graph']['adjlist']
    else:
        raise FileNotFoundError('Graph description not found')

    # generate graph
    if args.edges:
        graph = nx.parse_edgelist(graph_descr)
    else:
        graph = nx.parse_adjlist(graph_descr)

    # numeric conversion
    if args.numeric:
        # store valid substitutions only
        subs = {}
        for label in graph.nodes:
            try:
                subs[label] = int(label)
            except ValueError as _:
                if args.numeric == 'auto':
                    # abort if any conversion fails
                    break
        else:
            graph = nx.relabel_nodes(graph, subs)

    if args.timeline:
        print(Timeline(graph.nodes, evo['rounds']))

    if args.animate:
        ani = Animation2D(graph, evo['rounds'])
        #ani.save_as('infection.gif')

if __name__ == "__main__":
    main()
