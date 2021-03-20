import enum
import random
import textwrap
import typing

import networkx as nx

class Factory:

    class Template(enum.Enum):
        CYCLE = textwrap.dedent("""
                Graph whose nodes are connected in sequence; last
                node is connected to the first.

                Required keywords:
                - n: number of nodes (non-negative integer).
                """)
        CYCLE_U_ERDOS_RENYI = textwrap.dedent("""
                Union of a cycle graph and an Erdos-Renyi graph.

                Required keywords:
                - n: number of nodes (non-negative integer).
                - p: edges probability (float in [0,1]).

                Note: the probability p does not affect the cycle subgraph.
                """)
        CYCLE_U_PERFECT_MATCHING = textwrap.dedent("""
                Union of a cycle graph and a perfect matching graph.

                Required keywords:
                - n: number of nodes (even, non-negative integer).
                """)
        ERDOS_RENYI = textwrap.dedent("""
                Graph whose each pair of nodes is an edge with a given
                probability.

                Required keywords:
                - n: number of nodes (non-negative integer).
                - p: edges probability (float in [0,1]).
                """)
        TORUS = textwrap.dedent("""
                Graph whose nodes are arranged in a 2-dimensional lattice,
                wrapped along both axes; each node has four neighbors.

                Required keywords:
                - m: first dimension (non-negative integer).
                - n: second dimension (non-negative integer).
                """)

    def build(self, template: Template, **kwargs)-> typing.Optional[nx.Graph]:
        if template == __class__.Template.CYCLE:
            assert 'n' in kwargs
            n = kwargs['n']
            assert isinstance(n, int) and n >= 0

            return nx.cycle_graph(n)

        if template == __class__.Template.TORUS:
            assert 'm' in kwargs
            assert 'n' in kwargs
            m, n = kwargs['m'], kwargs['n']
            assert isinstance(m, int) and m >= 0
            assert isinstance(n, int) and n >= 0

            g = nx.grid_2d_graph(m, n, True)
            g = nx.relabel_nodes(g, {n:i for i,n in enumerate(g.nodes)})
            return g

        if template == __class__.Template.ERDOS_RENYI:
            assert 'n' in kwargs
            assert 'p' in kwargs
            n, p = kwargs['n'], kwargs['p']
            assert isinstance(n, int) and n >= 0
            assert isinstance(p, float) and 0 <= p <= 1

            return nx.erdos_renyi_graph(n, p)

        if template == __class__.Template.CYCLE_U_ERDOS_RENYI:
            assert 'n' in kwargs
            assert 'p' in kwargs
            n, p = kwargs['n'], kwargs['p']
            assert isinstance(n, int) and n >= 0
            assert isinstance(p, float) and 0 <= p <= 1

            return nx.compose(
                    self.build(__class__.Template.CYCLE, n=n),
                    self.build(__class__.Template.ERDOS_RENYI, n=n, p=p))

        if template == __class__.Template.CYCLE_U_PERFECT_MATCHING:
            assert 'n' in kwargs
            n = kwargs['n']
            assert isinstance(n, int) and n >= 0 and n % 2 == 0

            g = self.build(__class__.Template.CYCLE, n=n)
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
            #assert all(d == 3 for d in dict(g.degree).values())

            return g
