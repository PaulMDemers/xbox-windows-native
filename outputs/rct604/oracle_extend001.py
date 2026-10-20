"""Extend independent trace oracle for raw DIB header records."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'trace_oracle.py';s=p.read_text()
s=s.replace('14:2}','14:2,15:1}').replace('if api==14 else','if api in [14,15] else')
s=s.replace('totals=[];args={}','totals=[];args={};dibs={}')
anchor="  elif kind=='OUTPUT':"
branch="""  elif kind=='DIB':
   ident,address,status,count,stride,extent,*raw=v
   assert ident in calls and ident not in dibs and 'result' not in calls[ident]
   api=calls[ident]['api'];assert api in [4,11,15] and ident in args
   assert address==args[ident][{4:1,11:10,15:0}[api]]
   assert count==len(raw) and count in [0,1,10]
   expected=decode_header(address,raw,status)
   assert (status,stride,extent)==expected
   dibs[ident]=dict(address=address,status=status,raw=raw,stride=stride,extent=extent)
"""
assert anchor in s;s=s.replace(anchor,branch+anchor)
s=s.replace("  if api in [4,5,8]:assert ident in outputs","  if api in [4,11,15]:assert ident in dibs\n  if api in [4,5,8]:assert ident in outputs")
s=s.replace('outputs=outputs)','outputs=outputs,dibs=dibs)')
s=s.replace(' return dict(passed=True,total_pairs='," validate_headers(r)\n return dict(passed=True,header_records=len(r['dibs']),header_statuses=[d['status'] for d in r['dibs'].values()],total_pairs=")
p.write_text(s,newline='\n')
