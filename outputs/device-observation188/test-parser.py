"""Reject truncated/foreign/length-invalid observer evidence; retain actual query failures."""
from analyze import analyze
def blob(label,owner,typ,data):return f'{label} {owner} {typ} {len(data)} {data.hex()}\r\n'
s='XWN_DEVICE_OBSERVER 188 5 30000\r\n'
for i in range(5):
    s+=f'SAMPLE {i} {i*30000} 100\r\nINSTALL_STATE_BEGIN {i} 258 0\r\nPROCESS 50 1 0\r\n'
    s+=blob('PROCESS_IMAGE',50,0,b'rundll32.exe')+blob('COMMAND_UTF16',50,0,'rundll32.exe newdev.dll,ClientSideInstall PCI\\ABC'.encode('utf-16le'))
    s+='TOP 50 200 0 0 1 1 1 0\r\n'+blob('WINDOW_TEXT',200,0,b'Found New Hardware Wizard')
    s+=blob('DEVICE_ID',0,777,b'PCI\\ABC')+'DEVICE_STATUS 0 0 28\r\nDEVICE_STATUS_RESULT 0 0 777\r\nPROPERTY_UNAVAILABLE 0 4 13\r\nDEVICE_ENUM_END 1 259 0\r\n'
    s+='DRIVE 5 3 0\r\n'+blob('DRIVE_TARGET',5,0,b'\\Device\\Harddisk0\\Partition2')+'BYTES 5 0000000000100000 0000000000200000 0000000000100000\r\nCLUSTERS 5 8 512 256 512\r\n'
    s+=f'INSTALL_STATE_END {i} 258 0\r\nSAMPLE_COMPLETE {i} {i*30000+10} 0\r\n'
s+='COMPLETE 5 120010 0\r\nNO_RESTART_OR_DEVICE_ACTION 0 0 0\r\n'
r=analyze(s.encode());assert r['completed'] and r['samples'][0]['volumes'][0]['free_apis_agree']
assert r['samples'][0]['query_failures']==['PROPERTY_UNAVAILABLE 0 4 13']
assert r['samples'][0]['windows'][0]['window_text']=='Found New Hardware Wizard'
bad=[s.rsplit('COMPLETE 5',1)[0],s.replace('PROCESS_IMAGE 50 0 12','PROCESS_IMAGE 50 0 11'),s.replace('TOP 50','TOP 51'),s.replace('DEVICE_ENUM_END 1 259','DEVICE_ENUM_END 1 5'),s.replace('SAMPLE 1 30000','SAMPLE 2 30000')]
for data in bad:
    try:analyze(data.encode())
    except (AssertionError,ValueError,UnicodeError):pass
    else:raise AssertionError('Accepted damaged evidence')
print('Counted fields, window/process pairing, explicit missing properties and five malformed cases passed')
