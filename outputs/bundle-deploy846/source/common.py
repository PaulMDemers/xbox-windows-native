"""Shared Xbox 1.0 host-side preflight helpers. No launch or transfer methods."""
from __future__ import annotations

import ast
import ftplib
import hashlib
import ipaddress
import json
import os
import time
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STATE = Path(__file__).resolve().parents[1] / 'state'
LOCK = STATE / 'xbox10-deploy.lock'
ALLOWED_TARGET_IPS = {'192.168.50.242'}
F_OWNER_PATH = '/F/xwn-deploy-v1.json'
F_OWNER_VALUE = {
    'package_sha256': '0da2514ffa533b9fa52898d0ac9dc4c118abe17717dab6ab376f06010752a4bf',
    'purpose': 'XWN physical F native test v1',
}
F_OWNER_RECEIPT = ROOT / 'outputs/native-windows-physical-f/physical-cache-preflight.json'
F_OWNER_RECEIPT_SHA256 = 'fc9551c0fabaed3ade6025cac15f8390fa726ae2dd312b585df99c1af753f7bb'


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _ipv4(value: str) -> str:
    try:
        parsed = ipaddress.ip_address(value)
    except ValueError as exc:
        raise ValueError('Dashboard endpoint must be a literal IPv4 address') from exc
    if parsed.version != 4:
        raise ValueError('Dashboard endpoint must be IPv4')
    return str(parsed)


def load_private_config(path: Path) -> dict[str, str]:
    """Read JSON or literal os.environ.update(...) config without eval/exec."""
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError('Private connection config must be a regular local file')
    raw = path.read_bytes()
    if len(raw) > 1024 * 1024:
        raise ValueError('Private connection config size limit')
    if path.suffix.lower() == '.json':
        obj = json.loads(raw.decode('utf-8'))
        if not isinstance(obj, dict):
            raise ValueError('Connection config must be a JSON object')
        result = {k: obj.get(k) for k in ('host', 'user', 'password')}
    else:
        tree = ast.parse(raw.decode('utf-8-sig'), filename=str(path), mode='exec')
        matches = []
        for node in tree.body:
            if not isinstance(node, ast.Expr) or not isinstance(node.value, ast.Call):
                continue
            call = node.value
            if (isinstance(call.func, ast.Attribute) and call.func.attr == 'update'
                    and isinstance(call.func.value, ast.Attribute)
                    and call.func.value.attr == 'environ'
                    and isinstance(call.func.value.value, ast.Name)
                    and call.func.value.value.id == 'os'):
                matches.append(call)
        if len(matches) != 1:
            raise ValueError('Expected exactly one literal os.environ.update call')
        call = matches[0]
        vals = {}
        if call.args:
            if len(call.args) != 1:
                raise ValueError('Unsupported environment update')
            obj = ast.literal_eval(call.args[0])
            if not isinstance(obj, dict):
                raise ValueError('Environment update must use a literal dictionary')
            vals.update(obj)
        for keyword in call.keywords:
            if keyword.arg is None or keyword.arg in vals:
                raise ValueError('Invalid or duplicate environment setting')
            vals[keyword.arg] = ast.literal_eval(keyword.value)
        result = {k: vals.get(k) for k in ('XWN_FTP_HOST', 'XWN_FTP_USER', 'XWN_FTP_PASSWORD')}
        result = {'host': result['XWN_FTP_HOST'], 'user': result['XWN_FTP_USER'],
                  'password': result['XWN_FTP_PASSWORD']}
    if any(not isinstance(result[k], str) or not result[k] for k in result):
        raise ValueError('Connection config is missing a required field')
    result['host'] = _ipv4(result['host'])
    return result


def validate_endpoint(config: dict[str, str], dashboard_ip: str) -> str:
    expected = _ipv4(dashboard_ip)
    if expected not in ALLOWED_TARGET_IPS:
        raise ValueError('Dashboard IP is outside the reviewed Xbox 1.0 allowlist')
    if config['host'] != expected:
        raise ValueError('Private config host does not match operator-supplied dashboard IP')
    return expected


def check_shared_hardware_ticket():
    """Honor the existing serialized physical-work ticket; never create/close one here."""
    queue = ROOT / 'outputs/device-hardware220/state'
    claimed = queue / 'demo251-claimed.json'
    closed = queue / 'demo251-closed.json'
    if not claimed.is_file() or closed.exists():
        raise ValueError('Required existing demo251 hardware ticket is not active')
    current = json.loads(claimed.read_text(encoding='utf-8'))
    if current.get('owner') != 'demo251':
        raise ValueError('Hardware ticket owner mismatch')
    for other in queue.glob('*-claimed.json'):
        if other == claimed:
            continue
        other_closed = other.with_name(other.name.replace('-claimed.json', '-closed.json'))
        if not other_closed.exists():
            raise ValueError('Another physical hardware ticket is active: ' + other.stem)


@contextmanager
def deployment_lease(config_path: Path, dashboard_ip: str, *, ftp_factory=ftplib.FTP,
                     lock_path: Path = LOCK, timeout: int = 15,
                     ticket_check=check_shared_hardware_ticket):
    """Serialize our host clients, authenticate once, and close without logging secrets."""
    config = load_private_config(config_path)
    host = validate_endpoint(config, dashboard_ip)
    lock_path = Path(lock_path)
    ticket_check()
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fd = None
    ftp = None
    acquired = False
    try:
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        acquired = True
        os.write(fd, json.dumps({'host': host, 'pid': os.getpid(), 'started_unix': time.time()}).encode())
        os.fsync(fd)
        ftp = ftp_factory()
        ftp.connect(host, timeout=timeout)
        ftp.login(config['user'], config['password'])
        yield ftp, host
    finally:
        try:
            if ftp is not None:
                ftp.close()
        finally:
            if fd is not None:
                os.close(fd)
            if acquired:
                lock_path.unlink(missing_ok=True)


def verify_f_owner(ftp) -> dict:
    """Read and validate the pinned F-volume ownership marker (no mutation)."""
    receipt = F_OWNER_RECEIPT.read_bytes()
    if sha(receipt) != F_OWNER_RECEIPT_SHA256:
        raise ValueError('Pinned F-owner evidence receipt changed')
    obj = json.loads(receipt)
    if obj.get('ownership_marker') != F_OWNER_VALUE:
        raise ValueError('F-owner source receipt does not match embedded value')
    data = retrieve(ftp, F_OWNER_PATH, 4096)
    if json.loads(data.decode('utf-8')) != F_OWNER_VALUE:
        raise ValueError('F-volume owner marker mismatch')
    return {'path': F_OWNER_PATH, 'bytes': len(data), 'sha256': sha(data),
            'receipt_sha256': F_OWNER_RECEIPT_SHA256}


def retrieve(ftp, path: str, limit: int) -> bytes:
    if not (path.startswith('/E/') or path.startswith('/F/')) or limit < 0:
        raise ValueError('FTP RETR is restricted to explicit E/F paths')
    buf = bytearray()

    def receive(block: bytes):
        if len(buf) + len(block) > limit:
            raise ValueError('Remote file exceeded bounded RETR size')
        buf.extend(block)

    ftp.retrbinary('RETR ' + path, receive, 65536)
    return bytes(buf)


def retrieve_to_file(ftp, path: str, destination: Path, expected_size: int, limit: int):
    """Stream one selected E preimage to an exclusive local file and hash it."""
    import hashlib
    import stat
    destination = Path(destination)
    if not path.startswith('/E/') or expected_size < 0 or expected_size > limit:
        raise ValueError('Selected preimage exceeds its explicit size bound')
    if destination.exists() or destination.is_symlink():
        raise ValueError('Preimage destination already exists')
    digest = hashlib.sha256()
    count = 0

    def receive(block: bytes):
        nonlocal count
        count += len(block)
        if count > limit or count > expected_size:
            raise ValueError('Remote file exceeded listed size bound')
        out.write(block)
        digest.update(block)

    with destination.open('xb') as out:
        ftp.retrbinary('RETR ' + path, receive, 65536)
        out.flush()
        os.fsync(out.fileno())
    if count != expected_size:
        raise ValueError('FTP listing/RETR size mismatch')
    if not stat.S_ISREG(destination.stat().st_mode):
        raise ValueError('Captured preimage is not a regular file')
    return {'bytes': count, 'sha256': digest.hexdigest()}
