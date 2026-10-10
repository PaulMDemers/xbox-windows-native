"""Persistent, fail-closed hardware queue for the three authorized device chats."""
import argparse
import datetime
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATE = ROOT / 'state'
ORDER = ('audio', 'usb', 'pci')

def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def create(path, value):
    with path.open('x', encoding='utf-8') as handle:
        json.dump(value, handle, indent=2)
        handle.write('\n')

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('action', choices=('claim', 'close', 'inspect'))
parser.add_argument('name', nargs='?', choices=ORDER)
parser.add_argument('--report')
args = parser.parse_args()
STATE.mkdir(exist_ok=True)
if args.action == 'inspect':
    print(json.dumps({p.name: read(p) for p in sorted(STATE.glob('*.json'))}, indent=2))
else:
    if args.name is None:
        parser.error('name is required')
    claimed = STATE / (args.name + '-claimed.json')
    closed = STATE / (args.name + '-closed.json')
    if args.action == 'claim':
        for predecessor in ORDER[:ORDER.index(args.name)]:
            prior = STATE / (predecessor + '-closed.json')
            if not prior.exists() or read(prior).get('baseline_restored') is not True:
                raise SystemExit('WAIT: predecessor has not released restored console: ' + predecessor)
        if closed.exists():
            raise SystemExit('CLOSED: do not reuse this ticket')
        create(claimed, {'owner': args.name, 'claimed_utc': utc(), 'scope': 'device-hardware220'})
        print('CLAIMED: ' + args.name)
    else:
        if not claimed.exists() or read(claimed)['owner'] != args.name:
            raise SystemExit('No matching claim')
        report = Path(args.report or '')
        if not args.report or not report.is_absolute() or not report.is_file():
            raise SystemExit('An existing absolute report path is required')
        create(closed, {'owner': args.name, 'closed_utc': utc(), 'baseline_restored': True,
                        'report': str(report), 'declaration': 'Operator verified incoming baseline/startup restored and dashboard return'})
        print('CLOSED: ' + args.name)
