import matplotlib.pyplot as plt
import matplotlib.animation as ani
import networkx as nx

from infection.node import State
from infection.visualization.layout import Layout

_plot_settings = {
        # NODE SPECS
        #'with_labels': True,        # labels
        'node_shape':   'o',        # one of ‘so^>v<dph8'
        'node_size':    150,        # size
        'linewidths':    .4,        # node border width
        'edgecolors':   'k',        # node border color
        # EDGE SPECS
        'edge_color': 'grey',       # edge color
        'width':          .8,       # edge width
}

class Animation2D:

    def __init__(self, graph: nx.Graph, rounds: list,
                 layout: Layout=Layout.SPRING):
        self.graph = graph
        self.rounds = rounds
        self.layout = layout(self.graph)

        self.fig, self.ax = plt.subplots(figsize=(12,8))
        self.animation = ani.FuncAnimation(self.fig, self.__update__, \
                frames=len(self.rounds))

        plt.show()

    def __update__(self, num):
        # node colors
        infectious = self.rounds[num]['i']
        recovered = self.rounds[num]['r']
        colors = []
        for node in self.graph:
            if node in infectious:
                state = State.INFECTIOUS
            elif node in recovered:
                state = State.RECOVERED
            else:
                state = State.SUSCEPTIBLE
            colors.append(state.value['plt_col'])

        # plot
        self.ax.clear()
        nx.draw(self.graph, ax=self.ax, pos=self.layout, node_color=colors,
                **_plot_settings)

        self.ax.set_title("round %d" % num)

    def save_as(self, filename: str):
        self.animation.save(filename, writer='imagemagick')
