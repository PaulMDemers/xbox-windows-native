"""Owned-console HD prepare/apply/restore. Never launches Windows or edits startup."""
import argparse
import datetime
import importlib.util
import json
import os
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from hd_overlay import Package, PATHS, Refused, apply, prepare, require, restore, save, sha

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / 'outputs/demo-audio-level256/common001.py'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['prepare', 'apply', 'restore'])
    p.add_argument('--archive', type=Path, required=True)
    p.add_argument('--attempt', type=Path, required=True, help='Private unique directory; contains rollback binaries')
    p.add_argument('--receipt', type=Path, required=True, help='New small JSON record for this invocation')
    p.add_argument('--profile', choices=['720p', '1080i', 'baseline-restore'])
    args = p.parse_args()
    if (args.action == 'prepare') != (args.profile is not None):
        p.error('--profile is required only for prepare')
    require(not args.receipt.exists(), 'Receipt already exists; never reuse an invocation ID')
    require(not args.receipt.with_suffix('.tmp').exists(), 'Previous incomplete receipt exists')
    package = Package(args.archive, ROOT / 'tools/hd-overlay-0.2.0.json')
    # The adapter inherits the existing cooperative hardware ticket and exact console marker.
    package.pins[str(HELPER)] = sha(HELPER.read_bytes())
    identity = ROOT / 'outputs/native-windows-physical-f/physical-cache-preflight.json'
    package.pins[str(identity)] = sha(identity.read_bytes())
    spec = importlib.util.spec_from_file_location('physical256', HELPER)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    helper.ticket()
    for name in ['XWN_FTP_HOST', 'XWN_FTP_USER', 'XWN_FTP_PASSWORD']:
        require(bool(os.environ.get(name)), 'Missing environment variable: ' + name)
    receipt = {'action': args.action, 'attempt': str(args.attempt.resolve()),
               'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'status': 'starting', 'remote_writes_requested': args.action != 'prepare',
               'launch_requested': False, 'pins': package.pins}
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    save(args.receipt, receipt)
    lock = helper.queue / 'hd-overlay326-active.lock'
    fd = None
    try:
        # Never automatically reclaim a stale lock. A crashed owner needs inspection.
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.write(fd, json.dumps({'pid': os.getpid(), 'attempt': str(args.attempt.resolve())}).encode())
        os.fsync(fd)
        helper.ticket()
        with helper.connect(timeout=8) as ftp:
            receipt['console_marker_verified'] = True
            save(args.receipt, receipt)

            class Remote:
                def get(self, path):
                    require(path in package.baseline, 'Read outside declared inventory')
                    return helper.get(ftp, path)

                def put(self, path, data):
                    helper.ticket()
                    require(path in PATHS, 'Write outside six-file overlay')
                    helper.put(ftp, path, data)

            remote = Remote()
            if args.action == 'prepare':
                result = prepare(remote, package, args.attempt, args.profile)
            else:
                result = {'apply': apply, 'restore': restore}[args.action](remote, package, args.attempt)
            receipt.update(status='completed', transaction_state=result['state'],
                           incoming_profile=result['incoming_profile'], target_profile=result['target_profile'],
                           writes=result['writes'], restore_writes=result['restore_writes'],
                           protected_files=len(package.baseline), normal_startup_untouched=True)
    except BaseException as exc:
        # Do not write FTP exception strings: they may contain connection data.
        receipt.update(status='failed', error_type=type(exc).__name__)
        raise
    finally:
        receipt['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        try:
            save(args.receipt, receipt)
        finally:
            if fd is not None:
                os.close(fd)
                lock.unlink()
        print(json.dumps({key: value for key, value in receipt.items() if key != 'pins'}), flush=True)


if __name__ == '__main__':
    main()
