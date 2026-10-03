import json,pathlib
out=pathlib.Path(__file__).resolve().parent
parser=out.parent/'native-windows-nt5-interrupts/read-pdb-layouts.py'
ns={'__file__':str(parser)};exec(parser.read_text().split('selected={}')[0],ns)
selected={}
for name in ['_LOADER_PARAMETER_BLOCK','_LOADER_PARAMETER_EXTENSION','_LDR_DATA_TABLE_ENTRY']:
 item=ns['structs'][name].copy();item['fields']=ns['fields'](item['field_list']);selected[name]=item
(out/'handoff-pdb-layouts.json').write_text(json.dumps(selected,indent=2)+'\n')
print(json.dumps({n:{k:f['offset'] for k,f in v['fields'].items()} for n,v in selected.items()},indent=2))
