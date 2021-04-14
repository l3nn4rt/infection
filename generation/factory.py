import enum
import random

import networkx as nx


def _build_cycle(n: int):
    return nx.cycle_graph(n)


def _build_erdos_renyi(nodes: int, probability: float):
    return nx.erdos_renyi_graph(nodes, probability)


def _build_matching(nodes: int):
    node_ls = list(range(nodes))
    random.shuffle(node_ls)
    edges = zip(node_ls[:nodes//2], node_ls[nodes//2:])
    return nx.from_edgelist(edges)


def _build_cycle_erdos_renyi(nodes: int, probability: float):
    return nx.compose(
            nx.cycle_graph(nodes),
            nx.erdos_renyi_graph(nodes, probability))


def _build_cycle_matching(nodes: int):
    return nx.compose(
            nx.cycle_graph(nodes),
            _build_matching(nodes))


def _build_torus(columns: int, rows: int):
    g = nx.grid_2d_graph(columns, rows, True)
    g = nx.relabel_nodes(g, {n:i for i,n in enumerate(g.nodes)})
    return g


def _build_torus_erdos_renyi(columns: int, rows: int, probability: float):
    return nx.compose(
            _build_torus(columns, rows),
            _build_erdos_renyi(columns*rows, probability))


def _build_torus_matching(columns: int, rows: int):
    if (columns*rows) % 2 == 1:
        raise ValueError('odd number of nodes')
    return nx.compose(
            _build_torus(columns, rows),
            _build_matching(columns*rows))


class Factory:

    class Template(enum.Enum):

        CYCLE = {
            'help': "Graph whose nodes are connected in sequence; last node " \
                    "is connected to the first.",
            'vars': {
                'nodes': {
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
                'nodes': {
                    'help': 'number of nodes (non-negative integer)',
                    'type': int,
                    'test': lambda n: n >= 0
                },
                'probability': {
                    'help': 'edges probability (float in [0,1])',
                    'type': float,
                    'test': lambda p: 0 <= p <= 1
                }
            },
            'builder': _build_erdos_renyi
        }

        MATCHING = {
            'help': "Graph whose nodes have exactly one neighbor each.",
            'vars': {
                'nodes': {
                    'help': 'number of nodes (even, non-negative integer)',
                    'type': int,
                    'test': lambda n: n >= 0 and n % 2 == 0
                }
            },
            'builder': _build_matching
        }

        CYCLE_U_ERDOS_RENYI = {
            'help': "Union of a cycle graph and an Erdos-Renyi graph.",
            'vars': {
                'nodes': {
                    'help': 'number of nodes (non-negative integer)',
                    'type': int,
                    'test': lambda n: n >= 0
                },
                'probability': {
                    'help': 'edges probability (float in [0,1])',
                    'type': float,
                    'test': lambda p: 0 <= p <= 1
                }
            },
            'builder': _build_cycle_erdos_renyi
        }

        CYCLE_U_MATCHING = {
            'help': "Union of a cycle graph and a matching graph.",
            'vars': {
                'nodes': {
                    'help': 'number of nodes (even, non-negative integer)',
                    'type': int,
                    'test': lambda n: n >= 0 and n % 2 == 0
                }
            },
            'builder': _build_cycle_matching
        }

        TORUS = {
            'help': "Graph whose nodes are arranged in a 2-dimensional lattice, " \
                    "wrapped along both axes; each node has four neighbors",
            'vars': {
                'columns': {
                    'help': 'first dimension (non-negative integer)',
                    'type': int,
                    'test': lambda n: n >= 0
                },
                'rows': {
                    'help': 'second dimension (non-negative integer)',
                    'type': int,
                    'test': lambda n: n >= 0
                }
            },
            'builder': _build_torus
        }

        TORUS_U_ERDOS_RENYI = {
            'help': "Union of a torus graph and an Erdos-Renyi graph.",
            'vars': {
                'columns': {
                    'help': 'first dimension (non-negative integer)',
                    'type': int,
                    'test': lambda n: n >= 0
                },
                'rows': {
                    'help': 'second dimension (non-negative integer)',
                    'type': int,
                    'test': lambda n: n >= 0
                },
                'probability': {
                    'help': 'edges probability (float in [0,1])',
                    'type': float,
                    'test': lambda p: 0 <= p <= 1
                }
            },
            'builder': _build_torus_erdos_renyi
        }

        TORUS_U_MATCHING = {
            'help': "Union of a torus graph and a matching graph.",
            'vars': {
                'columns': {
                    'help': 'first dimension (non-negative integer)',
                    'type': int,
                    'test': lambda n: n >= 0
                },
                'rows': {
                    'help': 'second dimension (non-negative integer)',
                    'type': int,
                    'test': lambda n: n >= 0
                }
            },
            'builder': _build_torus_matching
        }


    def build(self, template: Template, **kwargs) -> nx.Graph:
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
