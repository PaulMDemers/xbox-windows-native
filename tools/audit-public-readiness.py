"""Read-only inventory of public-release review concerns in reachable Git blobs.

This is a triage aid, not a secret scanner, license audit or publication approval.
Reports locations/categories/object IDs without copying matched values.
"""
import argparse
import collections
import datetime
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = {
    'machine_path': rb'(?i)(?:[A-Z]:[\\/]Users[\\/][^\s\\/]+|/home/[^/\s]+)',
    'private_ipv4': rb'\b(?:192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b',
    'credential_literal_review': rb'''(?i)(?:password|passwd|pwd|ftp_pass)\s*[=:]\s*["'][^"'\r\n]+["']|\.login\(\s*["'][^\r\n]+''',
    'token_or_private_key': rb'gh[pousr]_[A-Za-z0-9]{25,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',
    'email_review': rb'\b[A-Za-z0-9_.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
}
BINARY_SUFFIXES = {'.iso', '.img', '.raw', '.qcow2', '.vhd', '.vhdx', '.exe', '.dll', '.sys', '.xbe', '.bin', '.zip', '.pdb', '.ram', '.pcap'}


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    a = parser.parse_args()
    if a.output.exists():
        parser.error('Use a new report path; existing reports are not replaced')
    # A blob may have several historical paths; rev-list gives one representative.
    objects = {}
    for line in git('rev-list', '--objects', '--all').decode().splitlines():
        oid, _, path = line.partition(' ')
        objects[oid] = path
    counts = collections.Counter()
    examples = collections.defaultdict(list)
    scanned = 0
    def finding(category, oid, path, line=None):
        counts[category] += 1
        if len(examples[category]) < 150:
            examples[category].append({'object': oid, 'representative_path': path, 'line': line})
    proc = subprocess.Popen(['git', '-C', str(ROOT), 'cat-file', '--batch'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    try:
        for oid, path in objects.items():
            proc.stdin.write((oid + '\n').encode()); proc.stdin.flush()
            header = proc.stdout.readline().decode().split()
            if len(header) != 3:
                raise RuntimeError('Invalid cat-file response')
            size = int(header[2])
            data = proc.stdout.read(size)
            if len(data) != size or proc.stdout.read(1) != b'\n':
                raise RuntimeError('Incomplete Git object read')
            if header[1] != 'blob':
                continue
            scanned += 1
            if Path(path).suffix.lower() in BINARY_SUFFIXES or b'\0' in data or data.startswith(b'MZ'):
                finding('binary_or_payload_review', oid, path)
            for category, pattern in PATTERNS.items():
                match = re.search(pattern, data)
                if match:
                    finding(category, oid, path, data[:match.start()].count(b'\n') + 1)
    finally:
        proc.stdin.close()
        proc.stdout.close()
        if proc.wait() != 0:
            raise RuntimeError('git cat-file failed')
    report = {
        'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'head': git('rev-parse', 'HEAD').decode().strip(),
        'scope': 'Unique blobs reachable from all local refs, including tags; representative paths only',
        'objects_enumerated': len(objects), 'blobs_scanned': scanned,
        'counts_unique_blobs_per_category': dict(counts), 'examples': dict(examples),
        'examples_limit_per_category': 150,
        'public_ready': False,
        'limitations': ['Pattern hits require human review; email may be an upstream author attribution.',
                       'Not a comprehensive secret detector or license/provenance determination.',
                       'Uncommitted, ignored, unreachable/reflog-only and remote-only objects excluded.',
                       'Git commit author metadata not classified; review it separately before publication.',
                       'No history, visibility, working files or credentials changed.']}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'blobs_scanned': scanned, 'counts': dict(counts), 'report': str(a.output)}))


if __name__ == '__main__':
    main()
