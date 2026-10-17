"""Private-byte comparison of retained third-reader output; no expected-byte edits."""
import json
from pathlib import Path
from ntfs_read002 import Reader,sha
K=Path(__file__).resolve().parent;source=Path('/home/paul/xbox-windows-native/clean-media404-oem001/disk.qcow2')
rows=json.loads((K/'third-reader002.json').read_text())['rows'];result=[]
with Reader(source) as reader:
 for i,row in enumerate(rows):
  node=reader.fs.mft.get(row['path']);attrs=node.attributes.find('',0x80);raw=reader.read(row['path']);reference=Path(f'/home/paul/xbox-windows-native/crypto423-reader002/file{i}.bin').read_bytes();assert len(raw)==len(reference)
  diff=[n for n,(a,b) in enumerate(zip(raw,reference)) if a!=b]
  headers=[a.header for a in attrs];assert len(headers)==1
  result.append({'path':row['path'],'bytes':len(raw),'attribute_flags':headers[0].flags,'compression_unit':headers[0].compression_unit,'valid_data_length':int(headers[0].header.Form.Nonresident.ValidDataLength),'difference_bytes':len(diff),'first_difference':min(diff),'last_difference':max(diff),'reference_differing_bytes_all_zero':all(reference[n]==0 for n in diff),'raw_sha256':sha(Path(f'/home/paul/xbox-windows-native/crypto423-reader002/file{i}.bin'))})
out=K/'compression-review001.json';assert not out.exists();out.write_text(json.dumps({'rows':result,'scope':'Raw Dissect versus independent NTFS-3G bytes; no proprietary bytes in report'},indent=2)+'\n');print(json.dumps(result))
