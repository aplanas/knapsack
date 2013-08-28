def read_file(filename, ratio=1, laplacian=True, as_int=True, remove_dot=False, with_time=False):
    """Read a file in the format <NUM> <PATH>."""
    item_list = []

    def _item(size, _time=None, path=None):
        if _time:
            return (size, tuple(int(t) for t in _time.split('-')), path)
        return (size, path)

    with open(filename) as f:
        for line in f:
            fields = line.split()
            
            if not with_time:
                size, path = fields[0], ' '.join(fields[1:])
                _time = None
            else:
                size, _time, path = fields[0], fields[1], ' '.join(fields[2:])

            if remove_dot:
                if path.startswith('.'):
                    path = path[1:]
            if path:
                # The +1 is some kind of laplacian smoothing aproximation.
                l = 1 if laplacian else 0
                l = 0
                # When coputing the KP is better to use int, and float
                # when groping.
                s = int(size) if as_int else float(size)
                item_list.append(_item(l+s/ratio, _time, path))

    return item_list
