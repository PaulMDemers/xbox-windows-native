"""Create a unique278 controller from frozen276; no preparation/launch."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'callback-inventory276'
review=json.loads((k/'source-review.json').read_text());assert review['passed']
names=['model.py','protocol.py','objects.py','oracle.py','proof.py','graph_base.py','graph_extra.py','terminal.py','backend.py','trace.py','prepare.py','Run.ps1','audit.py','analyze-disk-delta.py','atomic_json.py']
pins={}
def one(s,a,b):
 assert s.count(a)==1,a
 return s.replace(a,b)
for name in names:
 p=k/name;assert not p.exists();data=(old/name).read_bytes();pins[name]=hashlib.sha256(data).hexdigest()
 s=data.decode().replace('xwn276','xwn278').replace('callback-inventory276','texture-boundary278').replace('4764','4784').replace('4765','4785')
 if name=='prepare.py':
  s=s.replace('callback276-build003/xemu-callback276.exe','boundary278-build002/xemu-boundary278.exe').replace('7a19d5c3c3125b522cd7ca8699b1b6a78356f6b6976732a2c00de01be40de502',review['compiled_sha256']).replace('unique275','unique278')
 if name=='Run.ps1':s=s.replace('Consumed275','Consumed278')
 if name=='backend.py':
  s=one(s,"'cpu0_reason','cpu1_reason','cpu0_count','cpu1_count'","'cpu0_reason','cpu1_reason','admission278'")
  s=one(s,"    assert n['cpu0_done']==n['cpu1_done']==n['render_fenced']==n['display_fenced']==1","    assert n['texture278']==1 and 0<n['cpu0_count']==n['cpu1_count']<=128\n    assert n['cpu0_done']==n['cpu1_done']==n['render_fenced']==n['display_fenced']==1")
  s=one(s,"        self.r['initial_request_may_be_accepted']=True;self.save();self.set('xwn-ledger265','observe276')","        allocations=self.r['checkpoints'][-1]['state_header'][10:14]\n        self.r['attested_allocations278']=allocations\n        self.r['initial_request_may_be_accepted']=True;self.save();self.set('xwn-ledger265','textures278,'+','.join(map(str,allocations)))")
  s=one(s,"        inventory=self.get('xwn-callbacks276');self.r['callback_inventory_report']=inventory;self.save()\n",'')
  s=one(s,"        assert self.get('xwn-ledger265-report')==s\n        self.r['inventory_collection_completed']=True;self.save()\n        raise RuntimeError('Observation-only276 closed after initial refusal; no guest resume or observer arm')","        validate_report(s,1);assert self.get('xwn-ledger265-report')==s\n        self.check278('initial',1)")
  s=one(s,"        assert (self.root/'watch/terminal273.bin').is_file()","        self.check278('terminal',2)\n        assert (self.root/'watch/terminal273.bin').is_file()")
  s=one(s,'    def cleanup(self):',"""    def check278(self,key,stage):
        from proof import load_pages
        from decode import validate_graph
        rows=load_pages(self.out,self.r,key,stage,180000)
        result=validate_graph(rows,stage,self.r['attested_allocations278'])
        self.r[key+'_proof278']=result;self.save()
    def cleanup(self):""")
 if name=='proof.py':
  s=s.replace('import oracle,terminal,graph_base,graph_extra','import oracle,terminal,graph_base,graph_extra\nfrom decode import validate_graph')
  s=one(s,'set(range(50,64))','set(range(50,71))')
  s=one(s,"        a=graph_base.inspect([r for r in rows if r[0]<50],[r for r in ui if r[0]<50])","        boundary=validate_graph(rows,epoch,t['checkpoints'][0]['state_header'][10:14])\n        a=graph_base.inspect([r for r in rows if r[0]<50],[r for r in ui if r[0]<50])")
  s=one(s,'analyses.append(dict(base=a,extension=e))','analyses.append(dict(base=a,extension=e,boundary278=boundary))')
 p.write_text(s)
(k/'controller-lineage.json').write_text(json.dumps(dict(parent='closed276 sources only; never a runtime parent',inputs=pins,guest_prepared=False,guest_launched=False),indent=2)+'\n')
print('Unique278 controller written; no guest prepared/launched')
