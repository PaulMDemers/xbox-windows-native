"""Bounded UDP receiver. Packet validity does not authenticate a hardware result."""
import argparse
import datetime
import hashlib
import ipaddress
import json
from pathlib import Path
import socket
import struct
import time
import zlib

GROUPS = (('request', 72, 8), ('state', 104, 9), ('trace', 140, 63),
          ('pre', 392, 47), ('post', 580, 47))


def decode(packet, attempt, build_id):
    if len(attempt) != 16 or not any(attempt) or len(build_id) != 32 or not any(build_id):
        raise ValueError('invalid expected identity')
    if len(packet) != 772:
        raise ValueError('packet length')
    if packet[:8] != b'XWN655U1' or struct.unpack_from('<II', packet, 8) != (1, 772):
        raise ValueError('magic/version/length')
    if packet[16:32] != attempt or packet[32:64] != build_id:
        raise ValueError('unexpected attempt/build')
    if struct.unpack_from('<I', packet, 768)[0] != zlib.crc32(packet[:768]):
        raise ValueError('CRC')
    result, phase = struct.unpack_from('<iI', packet, 64)
    if result not in (-1, 0, 1) or phase not in (1, 2):
        raise ValueError('result/phase')
    groups = {name: list(struct.unpack_from('<' + 'I'*n, packet, offset))
              for name, offset, n in GROUPS}
    return dict(format_valid=True, hardware_execution_established=False,
                attempt=attempt.hex(), build_id=build_id.hex(), result=result,
                post_kind=phase, stage=groups['state'][0], error=groups['state'][1],
                pre_captured_raw=groups['pre'][0], post_captured_raw=groups['post'][0],
                **groups)


def validate_manifest(manifest):
    attempt = bytes.fromhex(manifest['attempt'])
    build_id = bytes.fromhex(manifest['build_id'])
    if len(attempt) != 16 or not any(attempt) or len(build_id) != 32 or not any(build_id):
        raise ValueError('invalid manifest identity')
    peer = str(ipaddress.IPv4Address(manifest['expected_peer']))
    if manifest['fixture'] not in ('host-loopback', 'physical-candidate'):
        raise ValueError('explicit fixture required')
    if manifest['fixture'] == 'host-loopback':
        if not ipaddress.IPv4Address(peer).is_loopback:
            raise ValueError('loopback fixture must use loopback address')
    else:
        digest = bytes.fromhex(manifest['candidate_sha256'])
        if len(digest) != 32 or not any(digest):
            raise ValueError('external executable pin required')
    return attempt, build_id, peer


def capture(sock, output, manifest, seconds=90, maximum=64):
    """Own a fresh evidence directory; caller owns/closes the socket.

    Receives only. Never sends an acknowledgment or requests another launch.
    Runs through the bound to detect conflicting valid records, even after one
    arrives. Peer address and tokens are correlation aids, not authentication.
    """
    attempt, build_id, peer = validate_manifest(manifest)
    if not 0 < seconds <= 180 or not 1 <= maximum <= 128:
        raise ValueError('capture bounds')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    def save(name, data):
        with (output/name).open('x', encoding='utf-8') as f:
            json.dump(data, f, indent=2); f.write('\n')
    save('manifest.json', manifest)
    report = dict(started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  fixture=manifest['fixture'], bound_seconds=seconds, packet_limit=maximum,
                  status='no-valid-packet', observations=[], duplicates=0,
                  hardware_execution_established=False, launch_sent=False)
    first = None
    end = time.monotonic() + seconds
    try:
        while len(report['observations']) < maximum:
            left = end-time.monotonic()
            if left <= 0:
                report['stop_reason']='deadline'; break
            sock.settimeout(left)
            try:
                packet, source = sock.recvfrom(65535)
            except socket.timeout:
                report['stop_reason']='deadline'; break
            index = len(report['observations'])
            # At most 512 KiB of raw packet data per capture, including junk.
            with (output/f'packet-{index:03d}.bin').open('xb') as f:
                f.write(packet[:4096])
            item = dict(source_ip=source[0], source_port=source[1], bytes=len(packet),
                        saved_bytes=min(len(packet),4096), sha256=hashlib.sha256(packet).hexdigest(),
                        received_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
            report['observations'].append(item)
            try:
                if source[0] != peer: raise ValueError('unexpected source IP')
                decoded = decode(packet, attempt, build_id)
            except ValueError as error:
                item.update(status='rejected', reason=str(error)); continue
            if first is None:
                first = packet; save('decoded.json', decoded)
                item['status']='first-valid'; report['status']='one-distinct-valid-record'
            elif packet == first:
                report['duplicates'] += 1; item['status']='duplicate'
            else:
                item['status']='conflicting-valid'; report['status']='conflicting-valid-records'
        else:
            report['stop_reason']='packet-limit'
    except BaseException as error:
        report.update(status='receiver-error', failure=repr(error)); raise
    finally:
        report['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
        save('summary.json', report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--bind', required=True)
    parser.add_argument('--port', required=True, type=int)
    parser.add_argument('--seconds', type=float, default=90)
    args = parser.parse_args()
    ipaddress.IPv4Address(args.bind)
    if not 1024 <= args.port <= 65535: parser.error('port must be 1024..65535')
    manifest = json.loads(args.manifest.read_text(encoding='utf-8'))
    validate_manifest(manifest)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((args.bind, args.port))
        result = capture(sock, args.output, manifest, args.seconds)
    print(json.dumps({key: result[key] for key in ('status','stop_reason','duplicates')}))
    return 0 if result['status']=='one-distinct-valid-record' else 2


if __name__ == '__main__':
    raise SystemExit(main())
