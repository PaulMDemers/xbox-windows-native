"""Independent context envelope decoder; physical provenance is external."""
import importlib.util,struct
from pathlib import Path
P=Path(__file__).resolve().parent
source=P/'capture_decode.py'
if not source.exists():source=P.parent/'cpu-context489/decode.py'
spec=importlib.util.spec_from_file_location('capture489_decoder',source);capture=importlib.util.module_from_spec(spec);spec.loader.exec_module(capture)
def decode(data,*,witness_address,frame_address,return_eips):
 def need(v,msg):
  if not v:raise ValueError(msg)
 need(len(data)==400,'envelope size')
 h=struct.unpack_from('<16I',data)
 need(h[:8]==(0x30393443,1,400,0x49000101,1,2,2,2),'envelope identity/boundaries/close')
 need(h[8]==witness_address and h[9]==frame_address and not any(h[10:]),'envelope source/frame/reserved')
 need(struct.unpack_from('<4I',data,384)==(0x454e4f44,1,0x49000101,400),'envelope trailer')
 records=[capture.decode(data[64:224]),capture.decode(data[224:384])]
 for i,r in enumerate(records):
  need(r['epoch']==i+1,'epoch order')
  need(r['return_eip']==return_eips[i],'capture return identity')
  need(r['entry_esp']==frame_address-44,'capture stack identity')
 need(records[0]['tsc_end']<=records[1]['tsc_start'],'boundary TSC reversed')
 return dict(records=records,preceding_witness_close=2,own_close_attested=False,later_paging_transition_attested=False,mapping_validated=False)
