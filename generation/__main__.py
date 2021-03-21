#!/usr/bin/env python3
# vim: ts=8 et sw=4 sts=4
"""
Generate graphs.
"""

import os

import networkx as nx

from infection.generation.factory import Factory

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
    f = Factory()

    # toroidal grids
    for m, n in [(5,20), (100, 100)]:
        g = f.build(Factory.Template.TORUS, m=m, n=n)

        g_dir = os.path.join(SAMPLES_DIR, 'toro-%d-%d' % (m, n))
        mkdir_p(g_dir)
        nx.write_adjlist(g, os.path.join(g_dir, 'graph.adjlist'))

    # graphs whose edges have a probability to exist
    for n, p in [(60, 0.10), (100, 0.05)]:
        er = f.build(Factory.Template.ERDOS_RENYI, n=n, p=p)

        er_dir = os.path.join(SAMPLES_DIR, 'erdos-renyi-%d-%0.2f' % (n, p))
        mkdir_p(er_dir)
        nx.write_adjlist(er, os.path.join(er_dir, 'graph.adjlist'))

        cer = f.build(Factory.Template.CYCLE_U_ERDOS_RENYI, n=n, p=p)
        cer_dir = os.path.join(SAMPLES_DIR, 'cycle-plus-erdos-renyi-%d-%0.2f' % (n, p))
        mkdir_p(cer_dir)
        nx.write_adjlist(cer, os.path.join(cer_dir, 'graph.adjlist'))

    # cycle with random perfect matching
    for n in [128, 256, 512]:
        g = f.build(Factory.Template.CYCLE_U_PERFECT_MATCHING, n=n)

        g_dir = os.path.join(SAMPLES_DIR, 'cycle-plus-perfect-matching-%d' % n)
        mkdir_p(g_dir)
        nx.write_adjlist(g, os.path.join(g_dir, 'graph.adjlist'))

if __name__ == "__main__":
    main()
