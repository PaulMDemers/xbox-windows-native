"""Request exact-match legacy DBG files from Microsoft's public symbol server."""
import hashlib,json,pathlib,sys,urllib.request,urllib.error
r=pathlib.Path(__file__).resolve().parents[2];sys.path.insert(0,str(r/'work/python-packages'))
import pefile
out=r/'outputs/native-windows-nt5';cache=r/'work/symbols';cache.mkdir(exist_ok=True)
records=[]
for flavor in ('EN_WIN2000_PRO_SP4','Windows 2000 (SP4)'):
    for name in ('ntoskrnl','hal'):
        path=r/'work/media-inspection'/flavor/(name+('.exe' if name=='ntoskrnl' else '.dll'))
        pe=pefile.PE(str(path));key=f'{pe.FILE_HEADER.TimeDateStamp:08X}{pe.OPTIONAL_HEADER.SizeOfImage:x}'
        record={'media':flavor,'image':path.name,'symbol_key':key,'attempts':[]}
        for ext in ('dbg','db_'):
            url=f'https://msdl.microsoft.com/download/symbols/{name}.dbg/{key}/{name}.{ext}'
            try:
                with urllib.request.urlopen(url,timeout=12) as response:data=response.read(20*1024*1024)
                target=cache/(flavor.replace(' ','_')+'-'+name+'.'+ext);target.write_bytes(data)
                record['attempts'].append({'url':url,'result':'downloaded','bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'file':str(target)})
                break
            except (urllib.error.URLError,TimeoutError) as error:
                record['attempts'].append({'url':url,'result':str(error)})
        records.append(record)
(out/'symbol-server-results.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps(records,indent=2))
