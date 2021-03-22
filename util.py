import os

def mkdir_p(path):
    """Emulate native `mkdir -p`."""
    acc = ''
    for d in path.split(os.sep):
        acc = os.path.join(acc, d)
        try:
            os.mkdir(acc)
        except OSError as e:
            # dir exists
            pass
