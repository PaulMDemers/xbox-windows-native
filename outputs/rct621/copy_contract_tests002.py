"""Reject the actual608 failure and independent tool-copy mutations."""
import copy,json
from pathlib import Path
from copy_contract import validate
K=Path(__file__).resolve().parent;out=K/'copy-contract-tests001.json';assert not out.exists()
read=lambda p:json.loads(p.read_text())
m=read(K/'media001.json');b=read(K/'build002.json');s=m['copy_script']
positive=validate(s,m['files'],b['rows'],621)
old=read(K.parent/'rct608/media001.json');oldbuild=read(K.parent/'rct608/build002.json')
try:validate(old['copy_script'],old['files'],oldbuild['rows'],608)
except AssertionError:pass
else:raise AssertionError('actual608 failure accepted')
line='copy D:\\RUN621.EXE C:\\xwn621-kit\\RUN621.EXE'
verify='C:\\xwn621-kit\\VERIFY621.EXE'
variants={
 'wrong_source':s.replace('D:\\RUN621.EXE','D:\\RUN606.EXE'),
 'wrong_destination':s.replace(line,line.replace('kit\\RUN621','kit\\RUN608')),
 'missing_copy':s.replace(line+'\r\nif errorlevel 1 goto fail\r\n',''),
 'duplicate_copy':s.replace(line,line+'\r\nif errorlevel 1 goto fail\r\n'+line),
 'missing_guard':s.replace(line+'\r\nif errorlevel 1 goto fail',line),
 'verifier_before_copies':s.replace('@echo off','@echo off\r\n'+verify+'\r\nif errorlevel 1 goto fail').replace('\r\n'+verify+'\r\nif errorlevel 1 goto fail\r\necho COPY','\r\necho COPY'),
 'missing_verifier':s.replace('\r\n'+verify+'\r\n','\r\n'),
}
rejected=['actual608_script']
for name,text in variants.items():
 try:validate(text,m['files'],b['rows'],621)
 except AssertionError:rejected.append(name)
 else:raise AssertionError(name)
for field in ['sha256','bytes']:
 bad=copy.deepcopy(m['files']);bad['RUN621.EXE'][field]='wrong' if field=='sha256' else 0
 try:validate(s,bad,b['rows'],621)
 except AssertionError:rejected.append('media_'+field)
 else:raise AssertionError(field)
out.write_text(json.dumps(dict(passed=True,positive=positive,rejected=rejected),indent=2)+'\n')
print('609 copy contract positive and',len(rejected),'rejections passed')
