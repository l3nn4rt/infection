import enum

import networkx as nx

class Layout(enum.Enum):

    CIRCULAR        = {'func': nx.circular_layout}
    KAMADA_KAWAI    = {'func': nx.kamada_kawai_layout}
    PLANAR          = {'func': nx.planar_layout}
    RANDOM          = {'func': nx.random_layout}
    SHELL           = {'func': nx.shell_layout}
    SPECTRAL        = {'func': nx.spectral_layout}
    SPIRAL          = {'func': nx.spiral_layout}
    SPRING          = {'func': nx.spring_layout}
