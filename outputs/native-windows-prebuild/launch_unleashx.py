"""Launch only our fixture Xromwell through the local guest FTP control port."""
import argparse,datetime,ftplib,json,pathlib
p=argparse.ArgumentParser();p.add_argument('--port',type=int,required=True);p.add_argument('--output',type=pathlib.Path,required=True)
a=p.parse_args()
record={'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':r'SITE EXEC E:\Apps\XWN\default.xbe'}
with ftplib.FTP() as ftp:
    record['server']=ftp.connect('127.0.0.1',a.port,timeout=8).splitlines()[-1]
    record['login_response']=ftp.login('xbox','xbox')
    # Record authorization and destination before the launch can close the socket.
    a.output.write_text(json.dumps(record,indent=2)+'\n')
    try:record['response']=ftp.sendcmd(record['command'])
    except (EOFError,ConnectionResetError,TimeoutError) as error:
        record['connection_after_launch']=type(error).__name__
    a.output.write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
