"""Read HAL partition telemetry from the owned xemu; no guest edits."""
import argparse,pathlib,json,sys,re
k=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(k.parent/'native-windows-prebuild'))
from monitor_capture import command,acquire_monitor_lock
p=argparse.ArgumentParser();p.add_argument('--state',type=pathlib.Path,required=True);p.add_argument('--rva',type=lambda s:int(s,0),required=True);p.add_argument('--port',type=int,default=4594);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
s=json.loads(a.state.read_text());base=int(next(m['base'] for m in s['modules'] if m['name']=='hal.dll'),0)
lock=acquire_monitor_lock(a.port)
try:text=command(a.port,'x /16wx '+hex(base+a.rva))
finally:lock.close()
values=[int(v,16) for line in text.splitlines() if re.match(r'^[0-9a-fA-F]+:',line) for v in re.findall(r'0x([0-9a-fA-F]{8})',line)]
assert len(values)==16 and values[0]==0x58575054
names=['magic','calls','stage','status','table_status','partition_count','length_low','length_high','returned_bytes','sector_size','has_brfr','legacy_length_attempted','legacy_status','legacy_start_low','legacy_length_low','legacy_length_high']
r=dict(zip(names,values));r['length_bytes']=values[6]+(values[7]<<32);r['hal_base']=hex(base);r['rva']=hex(a.rva);r['scope']='Read-only telemetry; no debugger edits'
a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
