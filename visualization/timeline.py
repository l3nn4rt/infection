def print_timeline(t, g):
    print('[%3d]' % t, ''.join([g.nodes[l]['state'].value['cli_str']
        for l in sorted(g, key=str)]))
