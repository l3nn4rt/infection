#!/usr/bin/env python3
# vim: ts=8 et sw=4 sts=4
"""
Generate graphs.
"""

import argparse
import hashlib
import os.path

import networkx as nx

from . import *
from .. import util


def main():
    parser = argparse.ArgumentParser(prog=__package__, description=__doc__)
    parser.add_argument('--graph-dir', metavar='PATH', help="""Graph directory
            path; this is created when needed. By default, use 'graphs' in the
            working directory).""", default='graphs', type=str)
    parser.add_argument('--save', help="""Save graph adjacency list in graph
            directory and return graph UID (file hash). See also '--graph-dir'
            for more info.""", action='store_true')
    subparsers = parser.add_subparsers(metavar= 'TEMPLATE', help="""Generate
            graph using TEMPLATE template. Available templates are: """ +
            str([*Factory.Template.__members__])[1:-1], required=True)

    # create a parser for each template
    for templ in Factory.Template:
        t_parser = subparsers.add_parser(templ.name,
                description=templ.value['help'])
        # store selected template
        t_parser.set_defaults(template=templ)

        templ_vars = templ.value['vars']
        # require specific arguments for each template
        for tv in templ_vars:
            value = templ_vars[tv]
            t_parser.add_argument('-' + tv[0], '--' + tv, help=value['help'],
                    type=value['type'], required=True)

    # parse sys.argv
    args = parser.parse_args()

    # extract template and its parameters
    templ = args.template
    templ_kwargs = {v: vars(args)[v] for v in templ.value['vars']}

    # create graph
    g = Factory().build(templ, **templ_kwargs)
    txt = '\n'.join(nx.generate_adjlist(g)) + '\n'

    if args.save:
        # we don't use nx.write_adjlist() because it adds a commment and this
        # behaviour can't be avoided; instead we create a file whose content
        # is the same text that would be printed on stdout
        file_hash = hashlib.sha1(txt.encode()).hexdigest()
        file_path = os.path.join(args.graph_dir, file_hash)

        try:
            util.mkdir_p(args.graph_dir)
            with open(file_path, 'w') as f:
                f.write(txt)
        except (NotADirectoryError, PermissionError) as e:
            util.die(__package__, e)

        print('Graph UID:', file_hash)
    else:
        print(txt, end='')

if __name__ == "__main__":
    main()
