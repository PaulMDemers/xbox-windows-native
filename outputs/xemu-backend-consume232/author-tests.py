"""New actual publication test with232 tuple fields; original231 inputs untouched."""
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'xemu-backend-publication231'
s=(old/'test-publication.c').read_text();s=s.replace('unsigned state, surfaces, dirty, downloaded, error, reason;', 'unsigned state, surfaces, dirty, downloaded, error, reason;\n        unsigned consume_stop,consume_steps,consume_words,wait_before,wait_after;')
s=s.replace('    qatomic_set(&d.preserve227.reason,n+4);', '    qatomic_set(&d.preserve227.reason,n+4);\n    qatomic_set(&d.preserve227.consume_stop,n+15);\n    qatomic_set(&d.preserve227.consume_steps,n+16);\n    qatomic_set(&d.preserve227.consume_words,n+17);\n    qatomic_set(&d.preserve227.wait_before,n+18);\n    qatomic_set(&d.preserve227.wait_after,n+19);')
assert 'consume_stop,n+15' in s
s=s.replace('    check(field(s,"error")==n+3 && field(s,"reason")==n+4);', '    check(field(s,"error")==n+3 && field(s,"reason")==n+4);\n    check(field(s,"consume_stop")==n+15 && field(s,"consume_steps")==n+16 && field(s,"consume_words")==n+17 && field(s,"wait_before")==n+18 && field(s,"wait_after")==n+19);')
s=s.replace('"bytes","error","reason",NULL', '"bytes","error","reason","consume_stop","consume_steps","consume_words","wait_before","wait_after",NULL')
p=k/'test-publication.c';assert not p.exists();p.write_text(s)
s=(old/'test-publication.py').read_text().replace('publication-test003','publication-test001')
p=k/'test-publication.py';assert not p.exists();p.write_text(s)
