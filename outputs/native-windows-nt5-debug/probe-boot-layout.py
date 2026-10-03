"""Compile boot/TSS offsets under each target's real flags; compare with PDB."""
import json,os,pathlib,re,shlex,subprocess
assert os.environ.get('XWN_BUILD_LEASE')=='held','Build lease required'
root=pathlib.Path('/home/paul/xbox-windows-native')
out=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-nt5-debug')
parser=out.parent/'native-windows-nt5-interrupts/read-pdb-layouts.py'
ns={'__file__':str(parser)};exec(parser.read_text().split('selected={}')[0],ns)
names=['_LOADER_PARAMETER_BLOCK','_LOADER_PARAMETER_EXTENSION','_I386_LOADER_BLOCK','_NLS_DATA_BLOCK','_PROFILE_PARAMETER_BLOCK','_CONFIGURATION_COMPONENT_DATA','_KTSS']
selected={}
for n in names:
 item=ns['structs'][n].copy();item['fields']=ns['fields'](item['field_list']);selected[n]=item
(out/'boot-pdb-layouts.json').write_text(json.dumps(selected,indent=2)+'\n')
aliases={'SetupLoaderBlock':'SetupLdrBlock','InfFileImage':'EmInfFileImage','InfFileSize':'EmInfFileSize','UnicodeCaseTableData':'UnicodeCodePageData'}
results={}
for label,dirname,target,sourceend,header in [('hal','hal-nt5','halxboxnt5','/hal/halx86/generic/halinit.c','hal.h'),('loader','loader','rosload','/boot/freeldr/freeldr/ntldr/winldr.c','freeldr.h')]:
 build=root/'build'/dirname
 commands=subprocess.check_output([str(root/'toolchains/RosBE-2.2.1/bin/ninja'),'-t','commands',target],cwd=build,text=True)
 line=next(l for l in commands.splitlines() if ' -c ' in l and l.endswith(sourceend));args=shlex.split(line)
 fields={};expected={}
 for n,item in selected.items():
  if n=='_KTSS' and label=='loader':continue
  typ=n[1:]
  for field,f in item['fields'].items():
   if typ=='KTSS' and field not in ['Esp0','IoMapBase','IoMaps','IntDirectionMap']:continue
   key=typ+'_'+field;fields[key]='FIELD_OFFSET('+typ+', '+aliases.get(field,field)+')';expected[key]=f['offset']
  fields[typ+'_size']='sizeof('+typ+')'
 src=build/'xwn-boot-layout.c';asm=build/'xwn-boot-layout.s'
 src.write_text('#include <'+header+'>\n'+''.join('const ULONG xwn_'+n+' = '+e+';\n' for n,e in fields.items()))
 cmd=[];i=0
 while i<len(args):
  if args[i] in ['-o','-c','-MF','-MT']:i+=2;continue
  if args[i] in ['-MD','-MMD']:i+=1;continue
  cmd.append(args[i]);i+=1
 cmd+=['-S','-o',str(asm),str(src)];subprocess.run(cmd,cwd=build,check=True)
 text=asm.read_text();values={}
 for n in fields:
  m=re.search(r'^_xwn_'+n+r':\s*\n\s*\.(long|space)\s+(\d+)',text,re.M);assert m,n
  values[n]=int(m[2]) if m[1]=='long' else 0
 checks=[{'field':n,'compiled':values[n],'windows':v,'matches':values[n]==v} for n,v in expected.items()]
 results[label]={'build_directory':str(build),'command':cmd,'values':values,'checks':checks,
  'sizes':{n[1:]:{'compiled':values[n[1:]+'_size'],'windows':v['size']} for n,v in selected.items() if n[1:]+'_size' in values}}
 (out/(label+'-boot-layout.c')).write_text(src.read_text());(out/(label+'-boot-layout.s')).write_text(text)
report={'scope':'Selected loader prefixes under actual HAL and rosload flags, plus TSS fields used by BIOS helpers. Size differences are recorded, not silently approved. No kernel handoff or BIOS execution.',
 'pdb_sha256':ns['hashlib'].sha256(ns['p']).hexdigest(),'targets':results}
(out/'boot-layout-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({n:{'checked':len(v['checks']),'mismatches':[c for c in v['checks'] if not c['matches']],'sizes':v['sizes']} for n,v in results.items()},indent=2))
assert all(c['matches'] for v in results.values() for c in v['checks'])

