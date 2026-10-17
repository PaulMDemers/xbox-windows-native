"""Explain ALL baseline-reader differences without modifying prior audit or source."""
import hashlib,json
from pathlib import Path
from ntfs_read002 import Reader,sha
K=Path(__file__).resolve().parent;P=Path('/home/paul/xbox-windows-native/crypto423-ntfs001')
oldfile=Path('/mnt/c/xwn405/extract004/files.json');newfile=P/'cold0-002/manifest.json'
old={r['path'].lower():r for r in json.loads(oldfile.read_text())};new=json.loads(newfile.read_text())
assert set(old)==set(new)
mismatch=[n for n in old if (old[n]['bytes'],old[n]['sha256'])!=(new[n]['bytes'],new[n]['sha256'])]
source=Path('/home/paul/xbox-windows-native/clean-media404-oem001/disk.qcow2');before=sha(source);rows=[]
with Reader(source) as reader:
 for name in mismatch:
  node=reader.fs.mft.get(name);attrs=node.attributes.find('',0x80);raw=reader.read(name)
  headers=[a.header for a in attrs];assert len(headers)==1 and not headers[0].resident
  header=headers[0].header.Form.Nonresident;valid=int(header.ValidDataLength);size=int(header.FileSize)
  assert 0<=valid<=size==len(raw)
  logical=raw[:valid]+bytes(size-valid)
  rows.append({'path':name,'bytes':size,'valid_data_length':valid,'raw_sha256':hashlib.sha256(raw).hexdigest(),'logical_zero_tail_sha256':hashlib.sha256(logical).hexdigest(),'prior_7zip_sha256':old[name]['sha256'],'matches_with_uninitialized_tail_zeroed':hashlib.sha256(logical).hexdigest()==old[name]['sha256']})
record={'raw_full_comparison_passed':not mismatch,'files':len(old),'raw_exact':len(old)-len(mismatch),'differences':rows,'source_unchanged':sha(source)==before,'original_manifest_sha256':sha(oldfile),'new_raw_manifest_sha256':sha(newfile),'prior_audit_unchanged':True,'scope':'Independent NTFS valid-data-length interpretation; raw reader audit is preserved, not rewritten'}
out=K/'reader-differences001.json';assert not out.exists();out.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({'raw_exact':record['raw_exact'],'differences':len(rows),'all_logical_match':all(r['matches_with_uninitialized_tail_zeroed'] for r in rows)}))
