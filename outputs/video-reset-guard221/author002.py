"""New protocol after preserved exported-reset ABI failure, never edit frozen001."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'protocol002-design.json';assert not dest.exists()
pins={}
def derive(old,new,changes):
 p=k/old;pins[old]=hashlib.sha256(p.read_bytes()).hexdigest();text=p.read_text()
 for a,b in changes:
  assert a in text,(old,a);text=text.replace(a,b)
 q=k/new;assert not q.exists();q.write_text(text,encoding='utf-8',newline='\n')
cases=[("['control001','candidate001']","['control002','candidate002']")]
derive('prepare.py','prepare002.py',cases+[("review['providers'][case]","review['providers'][case.replace('002','001')]"),("/case/'xboxbvid.dll'","/case.replace('002','001')/'xboxbvid.dll'")])
derive('Prepare.ps1','Prepare002.ps1',[("prepare.py","prepare002.py"),("'control001','candidate001'","'control002','candidate002'")])
derive('Run.ps1','Run002.ps1',[("'control001','candidate001'","'control002','candidate002'"),("frozen.json","frozen002.json")])
derive('trace.py','trace002.py',cases+[("review['providers'][case]","review['providers'][case.replace('002','001')]"),("/case/'xboxbvid.dll'","/case.replace('002','001')/'xboxbvid.dll'"),("case=='candidate001'","case=='candidate002'"),("'VidResetDisplay':8","'VidResetDisplay':4"),("row.update(kind='render_entry',function=name,state=state())","row.update(kind='render_entry',function=name,state=state());row['argument_words']=list(struct.unpack('<5I',g.read(regs['ESP']+4,20)))"),("# wrappers are stdcall, as verified by actual paired stack at return.","# NT5 exported reset wrapper takes no arguments (ret), other exports\n   # use their actual reviewed stdcall parameter count.")])
derive('audit.py','audit002.py',cases+[("r['limits']='Intentional debugger-mutated crash;", "r['limits']='Corrected002 ABI observer; intentional debugger-mutated crash;")])
derive('run.py','run002.py',cases+[("frozen.json","frozen002.json"),("case=='candidate001'","case=='candidate002'"),("k/'control001/host-state.json'","k/'control002/host-state.json'"),("str(k/'Run.ps1')","str(k/'Run002.ps1')"),("str(k/'trace.py')","str(k/'trace002.py')"),("/audit.py","/audit002.py")])
derive('freeze.py','freeze002.py',[("dest=k/'frozen.json'","dest=k/'frozen002.json'"),("for case in ['control001','candidate001']:","for case in ['control002','candidate002']:"),("/case/'xboxbvid.dll'","/case.replace('002','001')/'xboxbvid.dll'"),("k/'kernel-site-review.json']","k/'kernel-site-review.json',k/'calling-convention-review.json',k/'protocol002-design.json']")])
r={'scope':__doc__,'physical_access':False,'frozen001_unchanged':True,'prior_source_pins':pins,'reason':'Actual NT5 export XwnNt5VidResetDisplay@0 has ret with no pop. Private ResetDisplay cdecl remains4; exported fill24 and string8 actual return ESP deltas unchanged. Original control001 failure and seeded/erased guard retained. candidate001 prepared NEVER launched; new control002/candidate002 unique IDs and guards.','record_argument_words':True}
dest.write_text(json.dumps(r,indent=2)+'\n')
