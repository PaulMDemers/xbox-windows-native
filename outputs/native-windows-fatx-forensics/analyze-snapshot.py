"""Analyze captured physical FAT and directory entries without accessing the console."""
import array, collections, hashlib, json, pathlib, re, struct, sys
k = pathlib.Path(__file__).resolve().parent
out = k / 'artifacts/physical-013'
meta = (out / 'fat-metadata.bin').read_bytes()
fat = array.array('I', meta[4096:])
if sys.byteorder != 'little': fat.byteswap()
limit = 472764096 // 128
report = (out / 'snapshot.txt').read_text()
directories = {int(x) for x in re.findall(r'ENTRY parent=\d+ cluster=(\d+)', report)}
entries = []
owners = collections.defaultdict(list)
for directory in sorted(directories):
    b = (out / f'cluster-{directory:08x}.bin').read_bytes()
    for off in range(0, len(b), 64):
        e = b[off:off+64]
        if e[0] in (0, 255): break
        if e[0] == 229: continue
        assert 1 <= e[0] <= 42
        name = e[2:2+e[0]].decode('ascii', errors='replace')
        c, size = struct.unpack_from('<II', e, 44)
        item = dict(directory_cluster=directory, entry_offset=off, name=name,
                    first_cluster=c, size=size, is_directory=bool(e[1]&16))
        chain = []
        seen = set()
        while 1 <= c < limit and c not in seen:
            seen.add(c); chain.append(c); owners[c].append((directory, name))
            c = fat[c]
        item.update(clusters=len(chain), end_marker=f'{c:08x}',
                    chain_valid=c >= 0xfffffff8 or (size == 0 and not chain))
        if not item['is_directory']:
            item['capacity_sufficient'] = len(chain)*65536 >= size
        if name.lower() in ['xwnfatx.sys','xwnfatx.xwn-c11','cim.rep']:
            item['chain'] = chain
        entries.append(item)
driver = next(e for e in entries if e['name'].lower() == 'xwnfatx.sys')
cluster = (out / f"cluster-{driver['first_cluster']:08x}.bin").read_bytes()
prefix = k.parent/'native-windows-physical-f/artifacts/physical-013-filesystem-passive'
r = dict(scope=__doc__, metadata_sha256=hashlib.sha256(meta).hexdigest(),
         inspected_directory_clusters=sorted(directories), inspected_entries=len(entries),
         note='Only the captured directory clusters are enumerated; this is not a whole-volume audit.',
         invalid_entries=[e for e in entries if not e['chain_valid'] or not e.get('capacity_sufficient', True)],
         overlaps_in_captured_entries=[dict(cluster=c, owners=v) for c,v in owners.items() if len(v)>1],
         selected_entries=[e for e in entries if 'chain' in e],
         driver_cluster_matches_ftp_prefix=cluster == prefix.read_bytes(),
         driver_absolute_byte_offset=15633072*512+len(meta)+(driver['first_cluster']-1)*65536,
         driver_fat_neighborhood=[dict(cluster=c,next=f'{fat[c]:08x}') for c in range(driver['first_cluster']-4,driver['first_cluster']+8)])
(k/'physical-analysis.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
