import enum


class NodeState(enum.Enum):
    SUSCEPTIBLE = {
            'cli_str': '\033[1;34m*\033[0m',
            'plt_col': 'lightblue'
    }
    INFECTIOUS  = {
            'cli_str': '\033[1;31m*\033[0m',
            'plt_col': 'red'
    }
    RECOVERED   = {
            'cli_str': '\033[1;32m*\033[0m',
            'plt_col': 'green'
    }
