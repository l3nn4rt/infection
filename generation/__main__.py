#!/usr/bin/env python3
# vim: ts=8 et sw=4 sts=4
"""
Generate graphs.
"""

import argparse

import networkx as nx

from . import *


def main():
    parser = argparse.ArgumentParser(prog=__package__, description=__doc__)
    subparsers = parser.add_subparsers(metavar= 'TEMPLATE',
            help="""One from the available graph templates listed below.
            This must be specified exaclty as shown by the help command,
            (all capital letters and underscores).""", required=True)

    # create a parser for each template
    for templ in Factory.Template:
        t_parser = subparsers.add_parser(templ.name, help=templ.value['help'])
        # store selected template
        t_parser.set_defaults(template=templ)

        templ_vars = templ.value['vars']
        # require specific arguments for each template
        for tv in templ_vars:
            value = templ_vars[tv]
            t_parser.add_argument('-' + tv, help=value['help'],
                    type=value['type'], required=True)

    # parse sys.argv
    args = parser.parse_args()

    # extract template and its parameters
    templ = args.template
    templ_kwargs = {v: vars(args)[v] for v in templ.value['vars']}

    # create graph
    g = Factory().build(templ, **templ_kwargs)

    for line in nx.generate_adjlist(g):
        print(line)

if __name__ == "__main__":
    main()
