#!/usr/bin/env python3
# vim: ts=8 et sw=4 sts=4
"""
Simulate epidemic spreading in a SI[R][S]-model based network.
"""

import argparse
import hashlib
import json
import os
import random
import uuid

import networkx as nx

from . import *
from .. import util


def main():
    parser = argparse.ArgumentParser(prog=__package__, description=__doc__)
    # directory graphs are saved in
    parser.add_argument('--graph-dir', metavar='PATH',
            help="""Graph directory path; this is created when needed. By
            default, use 'graphs' in the working directory).""",
            type=str, default='graphs')
    # directory evolutions are saved in
    parser.add_argument('--evolution-dir', metavar='PATH',
            help="""Evolution directory path; this is created when needed. By
            default, use 'evolutions' in the working directory).""",
            type=str, default='evolutions')
    # how many evolutions to generate
    parser.add_argument('-c', '--count', metavar='NUM',
            help="""Generate NUM infection evolutions for each probability.
            By default, NUM is 1.""", type=int, default=1)
    # input graph:
    graph_g = parser.add_mutually_exclusive_group(required=True)
    # - by UID
    graph_g.add_argument('-g', '--graph-uid', metavar='UID',
            help="""Use graph wth given UID. Graph UID is used as file name and,
            by default, is the file hash. See also option '--graph-dir' for more
            info.""", type=str)
    # - from file
    graph_g.add_argument('-G', '--graph-file', metavar='FILE',
            help="""File containing the graph adjacency list or the graph edge
            list without data. If FILE is -, read standard input.""",
            type=argparse.FileType(), default=None)
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
    parser.add_argument('-n', '--numeric', metavar='WHEN',
            help="""Specify when to treat node labels as numbers. If WHEN is
            'always', perform conversion on any label for which it is possible,
            and treat as strings all the others. If WHEN is 'never', treat all
            node labels as strings. By default, perform conversion if all nodes
            can be treated as numbers, otherwise all labels will be treated as
            strings, in a "all-or-none" policy.""", choices=['always', 'never'],
            default='auto')
    # infection probability
    parser.add_argument('-p', '--probability', metavar='FIRST[,LAST[,COUNT]]',
            help="""Probability an infectious node has to infect nearby nodes
            on each round. If LAST is specified, generate multiple evolutions
            from different infection probability values. Use as infection
            probability each value from the linear space of COUNT evenly spaced
            samples in the interval [FIRST, LAST] (both sides included). START
            and STOP must be in range [0, 1]. By default, COUNT is 11.""",
            type=util.string_to_linspace)
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
    # - choose randomly
    zero_g.add_argument('-s', '--random-zeroes', metavar='NUM',
            help="""Select NUM nodes randomly as initially infectious nodes.
            NUM must be non-negative and not larger then the number of nodes in
            the graph.""", type=int)
    # save evolution instead of writing to standard output
    parser.add_argument('-w', '--save', help="""Save evolution in evolution
            directory and return evolution UID.
            See also '--evolution-dir' for more info.""",
            action='store_true')
    # human-friendly output for --save
    parser.add_argument('-v', '--verbose', help="""With '--save', print
            evolution directory and UID in a fancy way.""",
            action='store_true')
    # parse sys.argv
    args = parser.parse_args()

    # check args ranges
    if args.count < 0:
        util.die(__package__, ValueError(
            "count: NUM must be a non-negative integer"))
    if args.infection < 1:
        util.die(__package__, ValueError(
            "infection: ROUNDS must be a positive integer"))
    if min(args.probability) < 0 or max(args.probability) > 1:
        util.die(__package__, ValueError(
            "probability: FIRST and LAST must be in range [0, 1]"))
    if args.recovery is not None and args.recovery < 1:
        util.die(__package__, ValueError(
            "recovery: ROUNDS must be a positive integer"))

    # generate graph
    if args.graph_uid:
        try:
            graph_path = util.uid_to_path(args.graph_dir, args.graph_uid)
            graph_uid = os.path.splitext(os.path.basename(graph_path))[0]
            with open(graph_path) as f:
                graph_lines = f.readlines()
        except OSError as e:
            util.die(__package__, e)
    else:
        # graph file handled by argparse
        graph_path = args.graph_file.name
        graph_lines = args.graph_file.readlines()
        # compute graph UID when read from stdin
        graph_uid = hashlib.sha1(bytes(''.join(graph_lines),
                encoding='utf-8')).hexdigest()

    if args.edges:
        g = nx.parse_edgelist(graph_lines)
    else:
        g = nx.parse_adjlist(graph_lines)
    g.name = graph_uid

    # infectious nodes:
    if args.zero is not None:
        # read from args
        zeroes = set(x for x in args.zero.split(',') if x in g)
    elif args.random_zeroes is not None:
        # choose randomly later on
        if args.random_zeroes < 0 or args.random_zeroes > len(g.nodes):
            util.die(__package__, ValueError(
                "random zeroes: NUM must be in range [0, %s]" % len(g.nodes)))
        zeroes = set()
    else:
        # read from file
        lines = [l.split('#')[0].strip() for l in args.zero_file]
        zeroes = set(l for l in lines if l in g)

    # numeric conversion
    if args.numeric != 'never':
        subs = util.map_to_int(g.nodes, args.numeric == 'always')
        g = nx.relabel_nodes(g, subs)
        zeroes.update({subs[label] for label in subs if label in zeroes})
        zeroes.difference_update(subs)

    if args.save:
        try:
            evo_dir = util.make_dir_check_writable(args.evolution_dir)
        except OSError as e:
            util.die(__package__, e)

        if args.verbose:
            print('Evolution dir:', evo_dir)

    for prob in args.probability:
        for _ in range(args.count):
            # choose zeroes
            if args.random_zeroes is not None:
                zeroes = set(random.sample([*g.nodes], args.random_zeroes))

            evo_uid = make_evolution(
                    g, zeroes, prob, args.infection,
                    args.recovery, args.save, args.evolution_dir)

            if args.save:
                if args.verbose:
                    print('Evolution UID:', evo_uid)
                else:
                    print(evo_uid)


def make_evolution(
        graph, zeroes, infection_probability, infection_duration=1,
        recovery_duration=None, save=False, evolution_dir=os.path.curdir):

    evolution = Evolution(
            graph, zeroes, infection_probability,
            infection_duration, recovery_duration)

    evo_data = {}
    evo_data['graph-uid'] = graph.name
    evo_data['probability'] = infection_probability
    evo_data['rounds'] = evolution.rounds
    txt = json.dumps(evo_data)

    if save:
        # evolution UID consists of:
        # - a fixed graph UID prefix
        # - a random and (hopefully) unique string
        evo_uid = "%s-%s" % (graph.name[:8], uuid.uuid4().hex)
        evo_name = "%s.json" % evo_uid
        evo_path = os.path.join(evolution_dir, evo_name)

        try:
            with open(evo_path, 'w') as f:
                f.write(txt)
        except OSError as e:
            util.die(__package__, e)

        return evo_uid
    else:
        print(txt)
        return None


if __name__ == "__main__":
    main()
