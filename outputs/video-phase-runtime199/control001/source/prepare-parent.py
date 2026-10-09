"""Reuse immutable readback-equal183 parent of181, no fresh copy/old collection."""
from common import *
dest=k/'parent-copy.json';assert not dest.exists();old=k.parent/'video-dib-runtime183'
assert all(read(old/n/'closure.json')['closed'] for n in ['control001','candidate001'])
p=read(old/'parent-copy.json');assert p['virtual_disk_equal'] and p['metadata_only_rebase']
assert sha(Path(p['copied_path']))==p['copied_sha256']
for row in p['parents']:assert sha(Path(row['path']))==row['sha256']
p.update(reused_readback_verified_parent=True,prior_parent_record_sha256=sha(old/'parent-copy.json'),new_copy_performed=False,limits='Unmodified normally shut down181 parent, never183 control/candidate live disks. No old stage relaunched/collected.')
save(dest,p);print('Immutable readback-verified181 parent reused; original chains unchanged')
