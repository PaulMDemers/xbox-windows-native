"""Parameterize the exact337 preparation; keep its hive and payload checks intact."""
from pathlib import Path
import hashlib,json,difflib
W=Path(__file__).resolve().parents[2];K=W/'outputs/stock-installer343'
src=W/'outputs/stock-physical337/package.py';dst=W/'tools/package-stock-e.py';assert not dst.exists()
old=src.read_text();new=old
new=new.replace('import hashlib,json,shutil,struct,sys,zipfile','import argparse,hashlib,json,shutil,struct,sys,zipfile',1)
needle="K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('/mnt/e/xwn337/package001');dest=K/'package001.json'"
replacement="""W=Path(__file__).resolve().parents[1];K=W/'outputs/stock-physical337'
p=argparse.ArgumentParser(description='Prepare the reviewed private stock-E1080 profile from owned337 capture; no FTP or boot API.')
p.add_argument('--profile',choices=['stock-e-1080i'],required=True)
p.add_argument('--capture-root',type=Path,required=True)
p.add_argument('--hd-archive',type=Path,required=True)
p.add_argument('--boot-root',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--receipt',type=Path,required=True)
a=p.parse_args();P=a.output;dest=a.receipt
assert P.is_absolute() and P.parent.is_dir() and dest.parent.is_dir()
assert not P.is_symlink() and not P.exists() and not dest.exists()"""
assert new.count(needle)==1;new=new.replace(needle,replacement)
new=new.replace("shutil.disk_usage('/mnt/e')","shutil.disk_usage(P.parent)")
new=new.replace("source=Path('/mnt/e/xwn337/capture001');archive=Path('/mnt/e/Codex-archive/xbox-windows-native/0.2.0-recovered329/xwn-0.2.0-hd-overlay.zip')","source=a.capture_root;archive=a.hd_archive")
new=new.replace("Path('/mnt/e/xwn334/build001')","a.boot_root")
new=new.replace("limits='Local package only; no deployment or physical E boot. F installation and Xbox C untouched. Repeat boot validation remains prerequisite.'","profile=a.profile,limits='Private same-console F-to-E migration inputs only. No generic Windows-media installer or deployment. Physical342 scopes pass but combined/strict event gates FAIL. F rollback and Xbox C untouched.'")
assert new!=old and new.count('a.boot_root')==1
dst.write_text(new)
(K/'package-source.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='337/package.py',tofile='tools/package-stock-e.py')))
(K/'package-source-review.json').write_text(json.dumps(dict(original_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),derived_sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),hive_algorithm_unchanged=True,physical_access=False),indent=2)+'\n')
