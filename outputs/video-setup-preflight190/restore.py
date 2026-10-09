"""Offline fixture restore with explicit absent/existing/growth handling.

Disposable child only. This is not a guest FATX implementation or crash-atomic API.
Keep existing allocation when it fits; allocate a replacement chain before linking
and freeing the old chain when it does not. Directory attributes/timestamps survive.
"""
import struct

def restore(w, path, data):
    assert len(data) <= 0xffffffff
    parts = w.parts(path)
    parent = w.mkdir('/'.join(parts[:-1])) if len(parts) > 1 else 1
    d = w.directory(parent)
    old = d['entries'].get(parts[-1].lower())
    if old is None:
        w.write(path, data)
        return 'created'
    dc, off, entry = old
    assert not entry[1] & 16, 'Cannot replace a directory'
    chain = list(w.chain(struct.unpack_from('<I', entry, 44)[0]))
    growing = len(data) > len(chain) * w.p.cluster_size
    destination = w.allocate((len(data)+w.p.cluster_size-1)//w.p.cluster_size) if growing else chain
    for i, cluster in enumerate(destination):
        w.write_cluster(cluster, data[i*w.p.cluster_size:(i+1)*w.p.cluster_size])
    block = bytearray(w.read_cluster(dc))
    struct.pack_into('<II', block, off+44, destination[0], len(data))
    w.write_cluster(dc, block)
    if growing:
        for cluster in chain:
            w.fat[cluster] = 0
    w.dirs = {}
    assert w.read(path) == data
    return 'reallocated' if growing else 'in-place'
