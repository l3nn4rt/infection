import matplotlib.pyplot as plt
import matplotlib.animation as ani
import networkx as nx

from infection.node import NodeState

plot_settings = {
        # NODE SPECS
        'with_labels': True,        # labels
        'node_shape':   'o',        # one of ‘so^>v<dph8'
        'node_size':    150,        # size
        'linewidths':    .4,        # node border width
        'edgecolors':   'k',        # node border color
        # EDGE SPECS
        'edge_color': 'grey',       # edge color
        'width':          .8,       # edge width
}

class Animation2D:

    def __init__(self, graph, rounds):
        self.graph = graph
        self.rounds = rounds
        self.layout = nx.spring_layout(self.graph)

        self.fig, self.ax = plt.subplots(figsize=(12,8))
        self.animation = ani.FuncAnimation(self.fig, self.__update__, \
                frames=len(self.rounds))

        plt.show()

    def __update__(self, num):
        # node colors
        infectious = self.rounds[num]['infectious']
        recovered = self.rounds[num]['recovered']
        colors = []
        for node in self.graph:
            if node in infectious:
                state = NodeState.INFECTIOUS
            elif node in recovered:
                state = NodeState.RECOVERED
            else:
                state = NodeState.SUSCEPTIBLE
            colors.append(state.value['plt_col'])

        # plot
        self.ax.clear()
        nx.draw(self.graph, ax=self.ax, pos=self.layout, node_color=colors,
                **plot_settings)

        self.ax.set_title("round %d" % num)

    def save_as(self, filename: str):
        self.animation.save(filename, writer='imagemagick')
