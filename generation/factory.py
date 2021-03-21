import enum
import random
import typing

import networkx as nx


def _build_cycle(n: int):
    return nx.cycle_graph(n)


def _build_erdos_renyi(n: int, p: float):
    return nx.erdos_renyi_graph(n, p)


def _build_cycle_erdos_renyi(n: int, p: float):
    return nx.compose(
            nx.cycle_graph(n),
            nx.erdos_renyi_graph(n, p))


def _build_cycle_perfect_matching(n: int):
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
    #assert all(d == 3 for d in dict(g.degree).values())

    return g


def _build_torus(m: int, n: int):
    g = nx.grid_2d_graph(m, n, True)
    g = nx.relabel_nodes(g, {n:i for i,n in enumerate(g.nodes)})
    return g


class Factory:

    class Template(enum.Enum):

        CYCLE = {
            'help': "Graph whose nodes are connected in sequence; last node " \
                    "is connected to the first.",
            'vars': {
                'n': {
                    'help': 'number of nodes (non-negative integer)',
                    'type': int,
                    'test': lambda n: n >= 0
                }
            },
            'builder': _build_cycle
        }

        ERDOS_RENYI = {
            'help': "Graph whose each pair of nodes is an edge with " \
                    "a given probability",
            'vars': {
                'n': {
                    'help': 'number of nodes (non-negative integer)',
                    'type': int,
                    'test': lambda n:  n >= 0
                },
                'p': {
                    'help': 'edges probability (float in [0,1])',
                    'type': float,
                    'test': lambda p: 0 <= p <= 1
                }
            },
            'builder': _build_erdos_renyi
        }

        CYCLE_U_ERDOS_RENYI = {
            'help': "Union of a cycle graph and an Erdos-Renyi graph.",
            'vars': {
                'n': {
                    'help': 'number of nodes (non-negative integer)',
                    'type': int,
                    'test': lambda n: n >= 0
                },
                'p': {
                    'help': 'edges probability (float in [0,1])',
                    'type': float,
                    'test': lambda p: 0 <= p <= 1
                }
            },
            'builder': _build_cycle_erdos_renyi
        }

        CYCLE_U_PERFECT_MATCHING = {
            'help': "Union of a cycle graph and a perfect matching graph.",
            'vars': {
                'n': {
                    'help': 'number of nodes (even, non-negative integer)',
                    'type': int,
                    'test': lambda n: n >= 0 and n % 2 == 0
                }
            },
            'builder': _build_cycle_perfect_matching
        }

        TORUS = {
            'help': "Graph whose nodes are arranged in a 2-dimensional lattice, " \
                    "wrapped along both axes; each node has four neighbors",
            'vars': {
                'm': {
                    'help': 'first dimension (non-negative integer)',
                    'type': int,
                    'test': lambda n: n >= 0
                },
                'n': {
                    'help': 'second dimension (non-negative integer)',
                    'type': int,
                    'test': lambda n: n >= 0
                }
            },
            'builder': _build_torus
        }


    def build(self, template: Template, **kwargs)-> typing.Optional[nx.Graph]:
        """Build graph from template."""
        templ_vars = template.value['vars']

        for tv in templ_vars:
            info = templ_vars[tv]['help']

            if not tv in kwargs:
                raise KeyError(f"{tv} not found - {info}")

            if not isinstance(kwargs[tv], templ_vars[tv]['type']):
                raise TypeError(f"{tv} wrong type - {info}")

            if not templ_vars[tv]['test'](kwargs[tv]):
                raise ValueError(f"{tv} invalid value - {info}")

        return template.value['builder'](**kwargs)
