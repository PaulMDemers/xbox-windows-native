"""Collect one manual Paint run after dashboard return; no remote writes or launches."""
import argparse
import datetime
import ftplib
import hashlib
import io
import json
import os
import pathlib
import socket


class FTP(ftplib.FTP):
    def ntransfercmd(self, *args, **kwargs):
        sock, size = super().ntransfercmd(*args, **kwargs)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        return sock, size


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    root = pathlib.Path(__file__).resolve().parent
    record = root / 'physical-paint.json'
    trial = json.loads(record.read_text())
    assert trial['launch_attempted'] and not trial.get('collected_utc')
    assert not trial['startup_restart_enabled'] and not trial['startup_paint_enabled']
    folder = root / 'artifacts/paint-post'
    # Never mix evidence from two dashboard visits after a partial collection.
    folder.mkdir(exist_ok=False)
    result = dict(scope=__doc__,files={},hash_checks={},complete=False)
    report = root / 'paint-collection.json'
    assert not report.exists()

    def save():
        report.write_text(json.dumps(result, indent=2)+'\n')

    def get(ftp, path):
        buf = io.BytesIO()
        def receive(data):
            assert buf.tell()+len(data) <= 16*1024*1024
            buf.write(data)
        ftp.retrbinary('RETR '+path, receive, blocksize=65536)
        return buf.getvalue()

    checks = {
        'startup.cmd': ('/F/Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd',trial['startup_sha256']),
        'filesystem.sys': ('/F/winnt/system32/drivers/xwnfatx.sys',trial['filesystem_sha256']),
        'video.sys': ('/F/winnt/system32/drivers/xboxvnt5.sys',trial['miniport_sha256']),
        'previous-video.sys': (trial['miniport_backup'],trial['previous_miniport_sha256']),
        'hal.dll': ('/E/Applications/XWNFBoot/loader/halxboxnt5.dll',trial['hal_sha256']),
    }
    logs = {'trace.bin':'/F/winnt/system32/xwn-video-trace.bin',
            'system.evt':'/F/winnt/system32/config/SysEvent.Evt',
            'application.evt':'/F/winnt/system32/config/AppEvent.Evt'}
    try:
        with FTP() as ftp:
            ftp.connect('192.168.50.242', timeout=30)
            ftp.login('xbox',os.environ['XWN_FTP_PASSWORD'])
            owner=json.loads((root.parent/'native-windows-physical-f/physical-cache-preflight.json').read_text())['ownership_marker']
            assert json.loads(get(ftp,'/F/xwn-deploy-v1.json'))==owner
            for name,path in {**logs,**{n:v[0] for n,v in checks.items()}}.items():
                data=get(ftp,path)
                (folder/name).write_bytes(data)
                digest=hashlib.sha256(data).hexdigest()
                result['files'][name]=dict(path=path,bytes=len(data),sha256=digest)
                if name in checks:
                    result['hash_checks'][name]=dict(expected=checks[name][1],actual=digest,passed=digest==checks[name][1])
                save()
        result.update(complete=True,collected_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
        result['hashes_passed']=all(v['passed'] for v in result['hash_checks'].values())
        save()
        assert result['hashes_passed'], 'Preserved evidence; baseline hash mismatch requires review'
        trial.update(collected_utc=result['collected_utc'],collection_report=report.name)
        record.write_text(json.dumps(trial,indent=2)+'\n')
    except Exception as exc:
        result['error']=repr(exc)
        save()
        raise
    print('Collected Paint run. Event review and independent allocation/binary/hive audits remain pending.')


if __name__=='__main__':
    main()
