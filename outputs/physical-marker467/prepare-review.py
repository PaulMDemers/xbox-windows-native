"""Prepare read-only audit for the newly collected physical refusal."""
from pathlib import Path
K=Path(__file__).resolve().parent
s=(K.parent/'boot-refusal462/cold-review001.py').read_text()
s=s.replace("remote='/E/Applications/XWNBoot462a'","remote='/E/Applications/XWNBoot466a'").replace('-review462.json','-review467.json')
assert not (K/'cold-review001.py').exists();(K/'cold-review001.py').write_text(s)
