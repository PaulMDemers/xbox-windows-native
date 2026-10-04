"""Build an isolated xemu PCI resource model, restoring the borrowed build sources."""
import pathlib, subprocess, os, hashlib, json, shutil, difflib
assert os.environ.get('XWN_BUILD_LEASE') == 'held'
k=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-physical-f')
s=pathlib.Path('/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet')
image='ghcr.io/xemu-project/xemu-win64-toolchain-gcc@sha256:a4b2fb230a429d69272cb403de29c1a7a01aa63d84d92b427e6c7d119927aa73'
assert (s/'.source-revision').read_text().strip()=='e72e76bd1f12ce45c6c63b4196c6918ea2cc705d'
paths=[s/'hw/xbox/nv2a/nv2a.c',s/'hw/xbox/nv2a/nv2a_int.h']
original={p:p.read_bytes() for p in paths};patch=[]
try:
 p=paths[0];t=original[p].decode();needle='                             0, memory_region_size(d->vram));';assert t.count(needle)==1
 t=t.replace(needle,'''                             0, getenv("XWN_NV2A_RESOURCE_MODEL") ? 0x08000000 : memory_region_size(d->vram));''')
 needle='    memory_region_add_subregion(&d->mmio, 0x700000, &d->ramin);';assert t.count(needle)==1
 t=t.replace(needle,needle+'''
    /* Resource-allocation experiment only, not a complete hardware model.
     * "128-only" isolates BAR1 size; "128-plus-extra" also exposes the
     * physical registry's 512 KiB prefetchable BAR2 requirement. */
    if (getenv("XWN_NV2A_RESOURCE_MODEL") &&
        !strcmp(getenv("XWN_NV2A_RESOURCE_MODEL"), "128-plus-extra")) {
        memory_region_init_alias(&d->resource_test_bar2, OBJECT(d),
                                 "nv2a-resource-test-bar2", &d->ramin, 0, 0x80000);
        pci_register_bar(PCI_DEVICE(d), 2, PCI_BASE_ADDRESS_MEM_PREFETCH,
                         &d->resource_test_bar2);
    }
''');p.write_text(t)
 p=paths[1];t=original[p].decode();needle='    MemoryRegion vram_pci;';assert t.count(needle)==1
 p.write_text(t.replace(needle,needle+'\n    MemoryRegion resource_test_bar2;'))
 for p in paths:patch.extend(difflib.unified_diff(original[p].decode().splitlines(True),p.read_text().splitlines(True),fromfile='a/'+str(p.relative_to(s)),tofile='b/'+str(p.relative_to(s))))
 (k/'xemu-nv2a-resource-model.patch').write_text(''.join(patch))
 subprocess.run(['podman','run','--rm','--pull=never','-v',str(s)+':/src','-w','/src/build',image,'ninja','-j4','qemu-system-i386w.exe'],check=True)
 out=k/'artifacts/xemu-resource-model.exe';shutil.copyfile(s/'build/qemu-system-i386w.exe',out)
 result={'scope':__doc__,'source':'e72e76bd1f12ce45c6c63b4196c6918ea2cc705d','toolchain':image,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'patch_sha256':hashlib.sha256((k/'xemu-nv2a-resource-model.patch').read_bytes()).hexdigest()}
finally:
 for p,data in original.items():p.write_bytes(data)
 assert all(p.read_bytes()==data for p,data in original.items())
result['borrowed_sources_restored']=True
(k/'xemu-resource-model-build.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
