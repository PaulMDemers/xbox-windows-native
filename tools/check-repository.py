"""Check tracked payload exclusions before pushing source and reports."""
import json, pathlib, re, subprocess
root = pathlib.Path(__file__).resolve().parent.parent
files = subprocess.check_output(['git', '-C', str(root), 'ls-files', '-z']).decode().strip('\0').split('\0')
patterns = [rb'gh[pousr]_[A-Za-z0-9]{25,}', rb'-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----', rb'(?i)(?:productkey|product_key|hddkey|hdd_key)\s*[=:]\s*["\x27]?[A-Za-z0-9-]{12,}']
for name in files:
    p = root / name
    assert p.suffix.lower() not in {'.iso','.qcow2','.vhd','.vhdx','.img','.raw','.exe','.dll','.sys','.xbe','.bin','.zip','.pdb','.pcap','.ram'}, name
    data = p.read_bytes()
    assert b'\0' not in data and not data.startswith(b'MZ'), name
    assert len(data) < 5 * 1024 * 1024, name
    assert not any(re.search(pattern, data) for pattern in patterns), 'Credential pattern in ' + name
print(json.dumps({'tracked_files_checked':len(files),'binary_media_and_credential_pattern_checks_passed':True}))
