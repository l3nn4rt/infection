#!/usr/bin/env python3
# vim: ts=8 et sw=4 sts=4
"""
Generate graphs.
"""

import os
import random

import networkx as nx

SAMPLES_DIR = 'sample'

def mkdir_p(path):
    """Emulate native `mkdir -p`."""
    acc = ''
    for d in path.split(os.sep):
        acc = os.path.join(acc, d)
        try:
            os.mkdir(acc)
        except OSError as e:
            # dir exists
            pass


def main():
    # toroidal grids
    for m, n in [(5,20), (100, 100)]:
        g = nx.grid_2d_graph(m, n, True)
        g = nx.relabel_nodes(g, {n:i for i,n in enumerate(g.nodes)})
        g_dir = os.path.join(SAMPLES_DIR, 'toro-%d-%d' % (m, n))
        mkdir_p(g_dir)
        nx.write_adjlist(g, os.path.join(g_dir, 'graph.adjlist'))

    # graphs whose edges have a probability to exist
    for n, p in [(60, 0.10), (100, 0.05)]:
        er = nx.erdos_renyi_graph(n, p)
        er_dir = os.path.join(SAMPLES_DIR, 'erdos-renyi-%d-%0.2f' % (n, p))
        mkdir_p(er_dir)
        nx.write_adjlist(er, os.path.join(er_dir, 'graph.adjlist'))

        # add a cycle to the previous graph
        cer = nx.compose(nx.cycle_graph(n), er)
        cer_dir = os.path.join(SAMPLES_DIR, 'cycle-plus-erdos-renyi-%d-%0.2f' % (n, p))
        mkdir_p(cer_dir)
        nx.write_adjlist(cer, os.path.join(cer_dir, 'graph.adjlist'))

    # cycle with random perfect matching
    for n in [128, 256, 512]:
        g = nx.cycle_graph(n)
        # a valid matching is the diameters list
        matching = [(i, (i+n//2)%n) for i in range(n//2)]
        edge_indexes = list(range(len(matching)))
        # for n times, try to swap two random edges' ends
        for _ in range(n):
            i, j = random.sample(edge_indexes, 2)
            (a, b), (c, d) = matching[i], matching[j]
            # skip if (a,d) or (b,c) already exist
            if not a in g[d] and not b in g[c]:
                matching[i], matching[j] = (a, d), (c, b)
        g.add_edges_from(matching)
        assert all(d == 3 for d in dict(g.degree).values())
        g_dir = os.path.join(SAMPLES_DIR, 'cycle-plus-perfect-matching-%d' % n)
        mkdir_p(g_dir)
        nx.write_adjlist(g, os.path.join(g_dir, 'graph.adjlist'))

if __name__ == "__main__":
    main()
