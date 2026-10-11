"""Fault-check the audio oracle with independently generated sine-wave captures."""
import array,json,math,pathlib,subprocess,sys,wave
k=pathlib.Path(__file__).resolve().parent;out=k/'artifacts/capture-tests001';out.mkdir(parents=True,exist_ok=False)
cases=[]
for name,mode,count in [('valid','stereo',12),('silence','silence',12),('mono','mono',12),('swapped','swapped',12),('missing','stereo',11)]:
    data=array.array('h')
    for cycle in range(count):
        length=4800 if cycle%3==1 else 96000
        for i in range(length):
            l=round(1000*math.sin(2*math.pi*400*i/48000));r=round(700*math.sin(2*math.pi*600*i/48000))
            if mode=='silence':l=r=0
            if mode=='mono':r=l
            if mode=='swapped':l,r=r,l
            data.extend((l,r))
        data.extend([0]*33600)
    if sys.byteorder!='little':data.byteswap()
    path=out/(name+'.wav');report=out/(name+'.json')
    with wave.open(str(path),'wb') as w:w.setparams((2,2,48000,0,'NONE','not compressed'));w.writeframes(data.tobytes())
    subprocess.run([sys.executable,str(k/'analyze-capture.py'),str(path),str(report)],check=True,stdout=subprocess.DEVNULL)
    r=json.loads(report.read_text());assert r['passed']==(name=='valid'),name
    cases.append(dict(case=name,accepted=r['passed']))
(k/'capture-tests001.json').write_text(json.dumps(dict(passed=True,cases=cases,scope=__doc__,runtime_audio=False),indent=2)+'\n')
print('Audio oracle accepted valid stereo and rejected four signal faults')
