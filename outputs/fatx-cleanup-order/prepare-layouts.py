"""Adapt the tested offset compiler to this reviewed candidate's exact source and binary."""
import json
from pathlib import Path
k=Path(__file__).resolve().parent
b=json.loads((k/'binary-review.json').read_text());assert b['passed']
text=(k.parent/'fatx-shutdown-concurrency/compile-layouts.py').read_text()
text=text.replace('fatx-paging-eof-001','fatx-cleanup-order-001').replace('beeaf329f0446d3bdd2ed490fa8143888253115c0ff6c1662b67b82e6619eedd',b['sha256']).replace('873d6b4ff9505e71da119abd99aba301013e1749',b['source_tree']).replace('candidate0098','candidate0099')
target=k/'compile-layouts.py';assert not target.exists();target.write_text(text)
