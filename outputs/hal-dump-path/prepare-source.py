"""Add real fixed-root dump-path accounting, retaining paging and hibernate policy."""
import difflib,hashlib,json,os,subprocess,tempfile
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];prior=k.parent/'fatx-directory-order'
src=Path('/home/paul/xbox-windows-native/build/fatx-directory-order-001/source')
m=json.loads((prior/'manifest.json').read_text())
assert subprocess.check_output(['git','-C',str(src),'write-tree'],text=True).strip()==m['result_tree']
subprocess.run(['git','-C',str(src),'diff','--quiet'],check=True)
rel='hal/halx86/legacy/halpnpdd.c';old=(src/rel).read_text();new=old
assert hashlib.sha256((src/rel).read_bytes()).hexdigest()=='bf9c66a313a7c372c81fbe923d2681cf6487b14907154dd92b92eb8d8d24bbe0'
def replace(a,b):
    global new
    assert new.count(a)==1,a;new=new.replace(a,b)
replace('    LONG PagingPathCount;','    LONG PagingPathCount;\n    LONG DumpPathCount;')
helper='''#ifdef XBOX_NT5_HAL
/* A root usage removal must not underflow or transiently publish a negative
 * count; additions must not wrap. Separate counters preserve the obligations
 * of one special-file type when another type leaves the path. */
static NTSTATUS
HalpUpdateSpecialPathCount(PLONG Count, BOOLEAN InPath)
{
    LONG Current, Next;

    for (;;)
    {
        Current = InterlockedCompareExchange(Count, 0, 0);
        if (Current < 0 || (!InPath && Current == 0))
            return STATUS_INVALID_PARAMETER;
        if (InPath && Current == MAXLONG)
            return STATUS_INTEGER_OVERFLOW;
        Next = InPath ? Current + 1 : Current - 1;
        if (InterlockedCompareExchange(Count, Next, Current) == Current)
            return STATUS_SUCCESS;
    }
}
#endif

'''
replace('NTSTATUS\nNTAPI\nHalpDispatchPnp(',helper+'NTSTATUS\nNTAPI\nHalpDispatchPnp(')
start=new.index('                /* This fixed root bus and its power dispatch stay resident.')
end=new.index('                /* The root stays nonpageable',start)
new=new[:start]+'''                PLONG Count;

                /* This fixed root has no parent/power dependency, no idle
                 * registration and no hardware power-down operation. Its
                 * PnP/power dispatch lives in resident .text. Retain the root
                 * in D0 while either paging or crash-dump paths depend on it.
                 * Hibernation remains unsupported. This notification protects
                 * the root; it does not assert that a filesystem or miniport
                 * can already write a dump. Their own requests may still fail. */
                if (IoStackLocation->Parameters.UsageNotification.Type == DeviceUsageTypePaging)
                    Count = &PdoExtension->PagingPathCount;
                else if (IoStackLocation->Parameters.UsageNotification.Type == DeviceUsageTypeDumpFile)
                    Count = &PdoExtension->DumpPathCount;
                else
                {
                    Status = STATUS_NOT_SUPPORTED;
                    break;
                }

                Status = HalpUpdateSpecialPathCount(Count,
                    IoStackLocation->Parameters.UsageNotification.InPath);
                if (!NT_SUCCESS(Status))
                    break;

'''+new[end:]
needle='if (((PPDO_EXTENSION)FdoExtension)->PagingPathCount != 0)'
assert new.count(needle)==2
new=new.replace(needle,'if (((PPDO_EXTENSION)FdoExtension)->PagingPathCount != 0 ||\n                    ((PPDO_EXTENSION)FdoExtension)->DumpPathCount != 0)')
replace('''    else
    {
        PoStartNextPowerIrp(Irp);
        Irp->IoStatus.Status = STATUS_SUCCESS;''','''    else
    {
#ifdef XBOX_NT5_HAL
        /* The fixed Xbox root PDO never gates power or registers for idle
         * detection. Completing a power IRP does not take this root out of
         * D0, including while DumpPathCount or PagingPathCount is nonzero.
         * Child storage drivers retain their own power-path obligations. */
#endif
        PoStartNextPowerIrp(Irp);
        Irp->IoStatus.Status = STATUS_SUCCESS;''')
patch=k/'0102-hal-root-dump-path-accounting.patch';assert not patch.exists()
patch.write_bytes(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel)).encode())
with tempfile.TemporaryDirectory() as tmp:
    env=dict(os.environ,GIT_INDEX_FILE=tmp+'/index')
    subprocess.run(['git','-C',str(src),'read-tree',m['result_tree']],env=env,check=True)
    subprocess.run(['git','-C',str(src),'apply','--cached',str(patch)],env=env,check=True)
    tree=subprocess.check_output(['git','-C',str(src),'write-tree'],env=env,text=True).strip()
m.update(scope=__doc__,previous_tree=m['result_tree'],result_tree=tree,caveat='Root dump usage bookkeeping and lifetime protection only; full crash-dump write/recovery remains unqualified.')
m['patches'].append(str(patch.relative_to(ws)));(k/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
l=json.loads((prior/'inputs.json').read_text());l.update(result_tree=tree,manifest=str((k/'manifest.json').relative_to(ws)),manifest_json_sha256=hashlib.sha256(json.dumps(m,sort_keys=True,separators=(',',':')).encode()).hexdigest())
l['patch_sha256'][str(patch.relative_to(ws))]=hashlib.sha256(patch.read_bytes()).hexdigest()
boot=json.loads((k.parent/'reproducible-build/inputs.json').read_text())['profiles']['boot']
boot['targets']=['halxboxnt5'];boot['artifacts']={'hal/halx86/xboxnt5/halxboxnt5.dll':'halxboxnt5.dll'};l['profiles']={'boot':boot}
(k/'inputs.json').write_text(json.dumps(l,indent=2)+'\n')
(k/'build.py').write_text((prior/'build.py').read_text().replace('outputs/fatx-directory-order/inputs.json','outputs/hal-dump-path/inputs.json'))
(k/'artifacts').mkdir(exist_ok=True);(k/'artifacts/halpnpdd.c').write_text(new)
print(tree)
