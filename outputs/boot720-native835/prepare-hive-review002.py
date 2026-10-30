from pathlib import Path
import json
K=Path(__file__).resolve().parent
(K/'hive-review001-failure.json').write_text(json.dumps({'passed':False,'physical_access':False,'failure':'Missing libhivex.so.0 search path before any hive extracted or parsed','private_empty_directory':'C:/xwn835/hive-review001'},indent=2)+'\n')
p=K/'review-hives002.py';assert not p.exists();p.write_text((K/'review-hives.py').read_text().replace('review001','review002'))
