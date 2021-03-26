import math

from infection.node import State


class Timeline:

    def __init__(self, nodes, rounds) -> None:
        self.lines = []
        prefix_width = math.ceil(math.log10(len(rounds) + 1))
        for round_idx, round_dict in enumerate(rounds):
            line_lst = ['[%*d] ' % (prefix_width, round_idx)]
            for label in nodes:
                if label in round_dict['infectious']:
                    line_lst.append(State.INFECTIOUS.value['cli_str'])
                elif label in round_dict['recovered']:
                    line_lst.append(State.RECOVERED.value['cli_str'])
                else:
                    line_lst.append(State.SUSCEPTIBLE.value['cli_str'])
            self.lines.append(''.join(line_lst))

    def __str__(self):
        return '\n'.join(self.lines)
