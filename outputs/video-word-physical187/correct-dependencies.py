"""Preserve strict raw-byte dependency refusal; review only proven CRLF/LF difference and pin actual bytes."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'dependency002.py';assert not dest.exists()
p=k/'review-dependencies.py'
(k/'dependency001-refusal.json').write_text(json.dumps(dict(passed=False,physical_access=False,
    source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),failed_path='outputs/fatx0098-soak3/physical.py',
    reason='Raw committed LF versus existing working-copy CRLF mismatch; no dependency modified.'),indent=2)+'\n')
text=p.read_text().replace("dest=k/'dependency-review.json'","dest=k/'dependency002-review.json'")
text=text.replace('assert current==committed,name',"assert current.replace(b'\\r\\n',b'\\n')==committed.replace(b'\\r\\n',b'\\n'),name")
text=text.replace('matches_committed_head=True',"matches_committed_head_raw=current==committed,only_line_endings_differ=current!=committed,committed_sha256=hashlib.sha256(committed).hexdigest()")
text=text.replace('verifies unchanged committed dependencies, not a retroactive launch snapshot.',
    'pins actual dependency bytes and verifies no change beyond CRLF/LF; not a retroactive launch snapshot.')
text=text.replace('exactly match committed HEAD','match committed HEAD except recorded line endings')
dest.write_text(text,encoding='utf-8',newline='\n')
print('Strict dependency001 refusal retained; newline-only comparator prepared without dependency edits')
