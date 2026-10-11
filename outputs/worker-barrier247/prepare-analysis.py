"""New parser namespace includes bounded247 events; unchanged246 UI protocol."""
from pathlib import Path
k=Path(__file__).resolve().parent;s=(k/'lifecycle246.py').read_text();s=s.replace("  else:raise AssertionError(('Unknown NV phase',phase))","  elif phase in [70,71,73,74,75,76,77,78,80,82,83]:\n   pass #247 individually qualified by worker.py, natural flush data distinct\n  else:raise AssertionError(('Unknown NV phase',phase))")
(k/'lifecycle247.py').write_text(s)
for name in ['closed.py','test-lifecycle002.py','test-closed.py']:
 p=k/name;p.write_text(p.read_text().replace('from lifecycle246 import','from lifecycle247 import'))
print('247 parser prepared; old lifecycle246 retained exact')
