from infection.visualization import plot_basic
#import matplotlib.pyplot as plt

class Animation:
    def __init__(self, graph):
        self.g = graph

    def update(self):
        cols = [self.g.nodes[l]['state'].value['plt_col'] for l in self.g.nodes]
        #nx.draw(self.g, pos=nx.spring_layout(self.g),
        #        with_labels=True, node_color=cols)
        #plt.show()
        plot_basic.plot_graph(self.g, cols)
