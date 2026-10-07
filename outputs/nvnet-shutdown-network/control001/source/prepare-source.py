"""Keep the runtime-proven shutdown-reachable idle helper resident."""
import difflib,hashlib,json,os,subprocess,tempfile
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];prior=k.parent/'fatx-dump-map';src=Path('/home/paul/xbox-windows-native/build/fatx-dump-map-001/source')
read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
m=read(prior/'manifest.json');assert subprocess.check_output(['git','-C',str(src),'write-tree'],text=True).strip()==m['result_tree'];subprocess.run(['git','-C',str(src),'diff','--quiet'],check=True)
rel='drivers/network/dd/nvnet/nic.c';old=(src/rel).read_text();assert sha((src/rel).read_bytes())==read(k.parent/'controlled-dump-observe/callback-review.json')['source_sha256']['nic.c']
needle='''CODE_SEG("PAGE")
VOID
NvNetIdleTransmitter(
    _In_ PNVNET_ADAPTER Adapter,
    _In_ BOOLEAN ClearPhyControl)
{
    ULONG i;

    PAGED_CODE();'''
replacement='''/* MiniportShutdown reaches this helper during a bugcheck at HIGH_LEVEL.
 * Keep it resident; the existing bounded MMIO polling requires no paging. */
VOID
NvNetIdleTransmitter(
    _In_ PNVNET_ADAPTER Adapter,
    _In_ BOOLEAN ClearPhyControl)
{
    ULONG i;'''
assert old.count(needle)==1;new=old.replace(needle,replacement);patch=k/'0104-nvnet-resident-shutdown-helper.patch';assert not patch.exists()
patch.write_bytes(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel)).encode())
with tempfile.TemporaryDirectory() as tmp:
    env=dict(os.environ,GIT_INDEX_FILE=tmp+'/index');subprocess.run(['git','-C',str(src),'read-tree',m['result_tree']],env=env,check=True);subprocess.run(['git','-C',str(src),'apply','--cached',str(patch)],env=env,check=True);tree=subprocess.check_output(['git','-C',str(src),'write-tree'],env=env,text=True).strip()
m.update(scope=__doc__,previous_tree=m['result_tree'],result_tree=tree,caveat='Resident shutdown helper fixes an observed nested bugcheck; real dump writing and recovery remain unqualified until new tests.')
m['patches'].append(str(patch.relative_to(ws)));(k/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
profile={'support':{'definitions':{'ARCH':'i386','SARCH':'xbox','OARCH':'pentium','CMAKE_BUILD_TYPE':'Release','DBG':'OFF','KDBG':'OFF','PCH':'OFF','ENABLE_CCACHE':'OFF','XBOX_NT5_HAL':'ON','XBOX_NATIVE_PREFLIGHT':'OFF','XBOX_NATIVE_IO_PREFLIGHT':'OFF'},'targets':['nvnetnt5'],'artifacts':{'drivers/network/dd/nvnet/nvnetnt5.sys':'nvnetnt5.sys'}}}
l=read(prior/'inputs.json');l.update(result_tree=tree,manifest=str((k/'manifest.json').relative_to(ws)),manifest_json_sha256=sha(json.dumps(m,sort_keys=True,separators=(',',':')).encode()),profiles=profile);l['patch_sha256'][str(patch.relative_to(ws))]=sha(patch.read_bytes());(k/'inputs.json').write_text(json.dumps(l,indent=2)+'\n')
c=read(prior/'inputs.json');c['profiles']=profile;(k/'control-inputs.json').write_text(json.dumps(c,indent=2)+'\n')
for name,lock in [('build.py','inputs.json'),('build-control.py','control-inputs.json')]:
    (k/name).write_text((prior/'build.py').read_text().replace('outputs/fatx-dump-map/inputs.json','outputs/nvnet-shutdown-resident/'+lock))
(k/'artifacts').mkdir();(k/'artifacts/nic.c').write_text(new)
print(tree)
