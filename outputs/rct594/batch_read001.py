"""MIT. Read-only exact double-read verification with short-lived FTP sessions."""
import ftplib,time
def verify_batch(m,expected,record,out,key,limit_seconds=600):
    deadline=time.monotonic()+limit_seconds;f=None;used=0
    record.setdefault(key,{})
    try:
        for path,row in expected.items():
            for attempt in range(2):
                assert time.monotonic()<deadline,'Read-only verification deadline'
                try:
                    if f is None or used>=16:
                        if f is not None:f.close()
                        f=m.connect(timeout=15);used=0
                        record['read_sessions']=record.get('read_sessions',0)+1;m.write_json(out,record)
                    first=m.get(f,path);second=m.get(f,path);used+=1
                    assert first==second and len(first)==row['bytes'] and m.sha(first)==row['sha256'],path
                    record[key][path]=dict(bytes=len(first),sha256=m.sha(first));m.write_json(out,record)
                    break
                except (OSError,EOFError,ftplib.error_temp,ftplib.error_perm) as e:
                    code=str(e)[:3]
                    if isinstance(e,ftplib.error_perm) and code not in ('500','502'):raise
                    record.setdefault('read_failures',[]).append(dict(path=path,attempt=attempt+1,error_type=type(e).__name__,reply_code=code if code.isdecimal() else None))
                    m.write_json(out,record)
                    if f is not None:f.close();f=None
                    if attempt==1:raise
    finally:
        if f is not None:f.close()
