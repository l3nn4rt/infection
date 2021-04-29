#!/usr/bin/env python3
# vim: ts=8 et sw=4 sts=4
"""
Visualize epidemic spreading in a SI[R][S]-model based network.
"""

import argparse
import json

import networkx as nx

from . import *
from .. import util


def main():
    parser = argparse.ArgumentParser(prog=__package__, description=__doc__)
    # plot animation (default: false)
    parser.add_argument('-a', '--animate',
            help="""Animate the contagion; this is very CPU-intensive and not
            suitable for large graphs.""", action='store_true')
    # flag to read graph file as edge list (default: false)
    parser.add_argument('--edges',
            help="""Treat graph file as edge list. This option allows to ignore
            edge datas, but requires the edges to be written one per line.""",
            action='store_true')
    # directory evolutions are saved in
    parser.add_argument('--evolution-dir', metavar='PATH',
            help="""Evolution directory path; this is created when needed.
            By default, use 'evolutions' in the working directory.""",
            type=str, default='evolutions')
    # input evolution:
    evo_g = parser.add_mutually_exclusive_group(required=True)
    # - by UID
    evo_g.add_argument('-e', '--evolution-uid', metavar='UID',
            help="""Use evolution file with given UID. UID is the name of an
            evolution file, from the evolution directory, without extension.
            Any UID prefix matching a single evolution file is also accepted.
            See also option '--evolution-dir' for more info.""",
            type=str)
    # - from file
    evo_g.add_argument('-E', '--evolution-file', metavar='FILE',
            help="""Read evolution from FILE (absolute or relative path).
            If FILE is -, read standard input.""",
            type=argparse.FileType(), default=None)
    # directory graphs are saved in
    parser.add_argument('--graph-dir', metavar='PATH',
            help="""Graph directory path; this is created when needed.
            By default, use 'graphs' in the working directory.""",
            type=str, default='graphs')
    # input graph:
    graph_g = parser.add_mutually_exclusive_group()
    # - by UID
    graph_g.add_argument('-g', '--graph-uid', metavar='UID',
            help="""Use graph with given UID. UID is the name of a graph
            adjacency/edge list, from the graph directory, without extension.
            Any UID prefix matching a single graph file is also accepted.
            This option takes precedence over any graph UID found in the
            evolution file. See also option '--graph-dir' for more info.""",
            type=str)
    # - from file
    graph_g.add_argument('-G', '--graph-file', metavar='FILE',
            help="""File containing the graph adjacency list or the graph edge
            list without data.
            This option takes precedence over any graph UID found in the
            evolution file.""",
            type=argparse.FileType(), default=None)
    # plot layout
    parser.add_argument('-l', '--layout', metavar='LAYOUT',
            help="""Position nodes using LAYOUT layout. Available layouts are:
            """ + str([*Layout.__members__])[1:-1] + """. If LAYOUT is missing,
            default is 'SPRING'. Without '-a/--animation', this option has no
            effect.""", type=str, choices=Layout.__members__, default='SPRING')
    # try to save nodes as integers
    parser.add_argument('-n', '--numeric', metavar='WHEN',
            help="""Specify when to treat node labels as numbers. If WHEN is
            'always', perform conversion on any label for which it is possible,
            and treat as strings all the others. If WHEN is 'never', treat all
            node labels as strings. By default, perform conversion if all nodes
            can be treated as numbers, otherwise all labels will be treated as
            strings, in a "all-or-none" policy.""", choices=['always', 'never'],
            default='auto')
    # print timeline (default: false)
    parser.add_argument('-t', '--timeline',
            help="""Print node states at each round on the standard output; this
            option requires a color-capable terminal.""", action='store_true')
    # parse sys.argv
    args = parser.parse_args()

    # read evolution file
    if args.evolution_uid:
        try:
            evo_path = util.uid_to_path(args.evolution_dir, args.evolution_uid)
            with open(evo_path) as f:
                evo = json.load(f)
        except OSError as e:
            util.die(__package__, e)
    else:
        evo = json.load(args.evolution_file)

    # scan graph description sources in decreasing priority
    # - graph file handled by argparse
    if args.graph_file:
        graph_descr = args.graph_file
    # - graph by uid on command line
    elif args.graph_uid:
        try:
            graph_path = util.uid_to_path(args.graph_dir, args.graph_uid)
            with open(graph_path) as f:
                graph_descr = f.readlines()
        except OSError as e:
            util.die(__package__, e)
    # - graph by uid in evolution file
    elif 'graph-uid' in evo:
        try:
            graph_path = util.uid_to_path(args.graph_dir, evo['graph-uid'])
            with open(graph_path) as f:
                graph_descr = f.readlines()
        except OSError as e:
            util.die(__package__, e)
    # - legacy options
    elif 'graph-filename' in evo:
        with open(evo['graph-filename']) as f:
            graph_descr = f.readlines()
    elif 'graph-adjlist' in evo:
        graph_descr = evo['graph-adjlist']
    else:
        util.die(__package__, FileNotFoundError(
            'Graph description not found (use -g or -G)'))

    # generate graph
    if args.edges:
        graph = nx.parse_edgelist(graph_descr)
    else:
        graph = nx.parse_adjlist(graph_descr)

    # numeric conversion
    if args.numeric != 'never':
        subs = util.map_to_int(graph.nodes, args.numeric == 'always')
        graph = nx.relabel_nodes(graph, subs)

    if args.timeline:
        print(Timeline(graph.nodes, evo['rounds']))

    if args.animate:
        Animation2D(graph, evo['rounds'], Layout[args.layout])

if __name__ == "__main__":
    main()
