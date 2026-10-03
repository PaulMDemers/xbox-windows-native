"""Record the private emulator/package provenance without changing host packages."""
import hashlib,json,pathlib,subprocess
root=pathlib.Path('/home/paul/xbox-windows-native')
out=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-nt5')
records=[]
for kind in ('qemu-pc','7zip'):
    for path in sorted((root/'toolchains'/kind/'packages').glob('*.deb')):
        records.append({'toolchain':kind,'package':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                        'fields':subprocess.check_output(['dpkg-deb','-f',str(path),'Package','Version','Architecture'],text=True).strip()})
report={'package_source':'Authenticated Ubuntu resolute/resolute-updates archive metadata via apt download',
        'install_method':'dpkg-deb extraction under private task toolchain roots; no system package installation',
        'qemu_binary_sha256':hashlib.sha256((root/'toolchains/qemu-pc/root/usr/bin/qemu-system-i386').read_bytes()).hexdigest(),
        'packages':records}
(out/'runtime-provenance.json').write_text(json.dumps(report,indent=2)+'\n')
print(f'Recorded {len(records)} task-local packages')
