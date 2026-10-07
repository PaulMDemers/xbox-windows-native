import ftplib,time,json,pathlib,datetime,os
p=pathlib.Path('outputs/raw-c-inventory/physical-return.json');assert not p.exists()
for _ in range(12):
 f=ftplib.FTP()
 try:
  f.connect(os.environ['XWN_FTP_HOST'],timeout=3);f.login(os.environ['XWN_FTP_USER'],os.environ['XWN_FTP_PASSWORD']);f.quit();p.write_text(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),dashboard_returned=True),indent=2));print('Dashboard returned');break
 except (OSError,EOFError,ftplib.Error):f.close();time.sleep(3)
else:print('Still offline; no relaunch')
