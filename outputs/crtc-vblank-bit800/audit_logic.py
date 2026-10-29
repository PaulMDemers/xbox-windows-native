"""Independent 670-word physical result checks; models are not hardware evidence."""
from prefix_schema import validate as prefix_validate

TARGET=[719,779,719,0,738,770,719]
BASELINE=[1279,1649,1279,0,1389,1429,1279]

def validate(v):
 assert len(v)==670 and all(type(n)==int and 0<=n<=0xffffffff for n in v)
 code,forward=v[:2];before,checked,restored=v[76:83],v[83:90],v[90:97]
 attempted,count,first,mask,enabled,expected,observed=v[97:104]
 c4,c4check,c4restore,c4attempt,cm,c5,c5check,c5restore=v[104:112]
 c5target,c5attempt,c5after,c4after=v[112:116]
 c0,c0target,c0attempt,c0after,c0restore,zm,c4after0,c5after0=v[116:124]
 c2,c2target,c2attempt,c2after,c2restore,bm,c0after2,c4after2,c5after2=v[124:133]
 c3,c3target,c3attempt,c3after,c3restore,em,c0after3,c2after3,c4after3,c5after3=v[133:143]
 c5bbefore,c5btarget,c5battempt,c5bafter,c5bundo,nm,c0afterb,c2afterb,c3afterb,c4afterb=v[143:153]
 c17,c17target,c17attempt,c17after,c17undo,dm,c0after17,c2after17,c3after17,c4after17,c5after17=v[153:164]
 c1,c1target,c1attempt,c1after,c1undo,fm,c0after1,c2after1,c3after1,c4after1,c5after1,c17after1=v[164:176]
 c2bb,c2bt,c2ba,c2bv,c2bu,rm,c0after2b,c1after2b,c3after2b,c4after2b,c5after2b,c17after2b=v[176:188]
 c17bb,c17bt,c17ba,c17bv,c17bu,sm,c0after17b,c1after17b,c2after17b,c3after17b,c4after17b,c5after17b=v[188:200]
 c19bb,c19bt,c19ba,c19bv,c19bu,tm,c13b,c13v,c17v,c0v,c1v,c2v,c3v,c4v,c5v,c13u=v[200:216]
 c13before,c13target,c13attempt,c13after,c13undo,um,c19before13,c19after13,c17after13,c0after13,c1after13,c2after13,c3after13,c4after13,c5after13,c19undo13=v[216:232]
 vb,vt,va,vf,vu,vm=v[232:238]
 nb=[v[238+3*i] for i in range(6)];na=[v[239+3*i] for i in range(6)];nu=[v[240+3*i] for i in range(6)]
 assert va in [0,1] and 0<=vm<128
 if forward in [0x800,0x80022,0x80024,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e]:
  assert va==int([vb]+nb==[719,749,724,729,719,104,48])
  if va:
   assert vt==479 and vm==sum(1<<i for i,(a,b) in enumerate(zip([vu]+nu,[vb]+nb)) if a!=b)
   assert (vf==479 and na==nb)==(forward in [0x800,0x80024,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e])
  else:assert vt==vm==0 and vf==vu==0xffffffff and na==nu==[0xffffffff]*6 and forward==0x80022
 else:assert v[232:238]==[0,0,0,0xffffffff,0xffffffff,0] and v[238:256]==[0,0xffffffff,0xffffffff]*6
 qb,qt,qa,qf,qu,qm=v[256:262]
 qnb=[v[262+3*i] for i in range(6)];qna=[v[263+3*i] for i in range(6)];qnu=[v[264+3*i] for i in range(6)]
 assert qa in [0,1] and 0<=qm<128
 if forward in [0x800,0x80024,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e]:
  assert qa==int([qb]+qnb==[749,479,724,729,719,104,48])
  if qa:
   assert qt==524 and qm==sum(1<<i for i,(a,b) in enumerate(zip([qu]+qnu,[qb]+qnb)) if a!=b)
   assert (qf==524 and qna==qnb)==(forward in [0x800,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e])
  else:assert qt==qm==0 and qf==qu==0xffffffff and qna==qnu==[0xffffffff]*6 and forward==0x80024
 else:assert v[256:262]==[0,0,0,0xffffffff,0xffffffff,0] and v[262:280]==[0,0xffffffff,0xffffffff]*6
 wb,wt,wa,wf,wu,wm=v[280:286]
 wnb=[v[286+3*i] for i in range(8)];wna=[v[287+3*i] for i in range(8)];wnu=[v[288+3*i] for i in range(8)]
 assert wa in [0,1] and 0<=wm<512
 if forward in [0x800,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e]:
  assert wa==int([wb]+wnb==[719,479,524,724,729,0,719,104,48])
  if wa:
   assert wt==479 and wm==sum(1<<i for i,(a,b) in enumerate(zip([wu]+wnu,[wb]+wnb)) if a!=b)
   assert (wf==479 and wna==wnb)==(forward in [0x800,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e])
  else:assert wt==wm==0 and wf==wu==0xffffffff and wna==wnu==[0xffffffff]*8 and forward==0x80026
 else:assert v[280:286]==[0,0,0,0xffffffff,0xffffffff,0] and v[286:310]==[0,0xffffffff,0xffffffff]*8
 xb,xt,xa,xf,xu,xm=v[310:316]
 xnb=[v[316+3*i] for i in range(8)];xna=[v[317+3*i] for i in range(8)];xnu=[v[318+3*i] for i in range(8)]
 assert xa in [0,1] and 0<=xm<512
 if forward in [0x800,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e]:
  assert xa==int([xb]+xnb==[0,479,524,479,724,729,719,104,48])
  if xa:
   assert xt==0 and xm==sum(1<<i for i,(a,b) in enumerate(zip([xu]+xnu,[xb]+xnb)) if a!=b)
   assert (xf==0 and xna==xnb)==(forward in [0x800,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e])
  else:assert xt==xm==0 and xf==xu==0xffffffff and xna==xnu==[0xffffffff]*8 and forward==0x80028
 else:assert v[310:316]==[0,0,0,0xffffffff,0xffffffff,0] and v[316:340]==[0,0xffffffff,0xffffffff]*8
 yb,yt,ya,yf,yu,ym=v[340:346]
 ynb=[v[346+3*i] for i in range(8)];yna=[v[347+3*i] for i in range(8)];ynu=[v[348+3*i] for i in range(8)]
 assert ya in [0,1] and 0<=ym<512
 if forward in [0x800,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e]:
  assert ya==int([yb]+ynb==[724,479,524,479,0,729,719,104,48])
  if ya:
   assert yt==489 and ym==sum(1<<i for i,(a,b) in enumerate(zip([yu]+ynu,[yb]+ynb)) if a!=b)
   assert (yf==489 and yna==ynb)==(forward in [0x800,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e])
  else:assert yt==ym==0 and yf==yu==0xffffffff and yna==ynu==[0xffffffff]*8 and forward==0x8002a
 else:assert v[340:346]==[0,0,0,0xffffffff,0xffffffff,0] and v[346:370]==[0,0xffffffff,0xffffffff]*8
 eb,et,ea,ef,eu,emsk=v[370:376]
 enb=[v[376+3*i] for i in range(8)];ena=[v[377+3*i] for i in range(8)];enu=[v[378+3*i] for i in range(8)]
 assert ea in [0,1] and 0<=emsk<512
 if forward in [0x800,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e]:
  assert ea==int([eb]+enb==[729,479,524,479,0,489,719,104,48])
  if ea:
   assert et==492 and emsk==sum(1<<i for i,(a,b) in enumerate(zip([eu]+enu,[eb]+enb)) if a!=b)
   assert (ef==492 and ena==enb)==(forward in [0x800,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e])
  else:assert et==emsk==0 and ef==eu==0xffffffff and ena==enu==[0xffffffff]*8 and forward==0x8002c
 else:assert v[370:376]==[0,0,0,0xffffffff,0xffffffff,0] and v[376:400]==[0,0xffffffff,0xffffffff]*8
 vb2,vt2,va2,vf2,vu2,vm2=v[400:406]
 vn2=[v[406+3*i] for i in range(8)];vfns=[v[407+3*i] for i in range(8)];vuns=[v[408+3*i] for i in range(8)]
 assert va2 in [0,1] and 0<=vm2<512
 if forward in [0x800,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e]:
  assert va2==int([vb2]+vn2==[719,479,524,479,0,489,492,104,48])
  if va2:
   assert vt2==479 and vm2==sum(1<<i for i,(a,b) in enumerate(zip([vu2]+vuns,[vb2]+vn2)) if a!=b)
   assert (vf2==479 and vfns==vn2)==(forward in [0x800,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e])
  else:assert vt2==vm2==0 and vf2==vu2==0xffffffff and vfns==vuns==[0xffffffff]*8 and forward==0x8002e
 else:assert v[400:406]==[0,0,0,0xffffffff,0xffffffff,0] and v[406:430]==[0,0xffffffff,0xffffffff]*8
 cb7,ct7,ca7,cf7,cu7,cm7=v[430:436]
 cn7=[v[436+3*i] for i in range(8)];cfns7=[v[437+3*i] for i in range(8)];cuns7=[v[438+3*i] for i in range(8)]
 assert ca7 in [0,1] and 0<=cm7<512
 if forward in [0x800,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e]:
  assert ca7==int([cb7]+cn7==[240,236,96,212,207,207,237,255,16])
  if ca7:
   assert ct7==116 and (cb7^ct7)==0x84
   assert cm7==sum(1<<i for i,(a,b) in enumerate(zip([cu7]+cuns7,[cb7]+cn7)) if a!=b)
   assert (cf7==116 and cfns7==cn7)==(forward in [0x800,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e])
  else:assert ct7==cm7==0 and cf7==cu7==0xffffffff and cfns7==cuns7==[0xffffffff]*8 and forward==0x80030
 else:assert v[430:436]==[0,0,0,0xffffffff,0xffffffff,0] and v[436:460]==[0,0xffffffff,0xffffffff]*8
 cb10,ct10,ca10,cf10,cu10,cm10=v[460:466]
 cn10=[v[466+3*i] for i in range(8)];cfns10=[v[467+3*i] for i in range(8)];cuns10=[v[468+3*i] for i in range(8)]
 assert ca10 in [0,1] and 0<=cm10<512
 if forward in [0x800,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e]:
  assert ca10==int([cb10]+cn10==[212,236,116,96,207,207,237,255,16])
  if ca10:
   assert ct10==233
   assert cm10==sum(1<<i for i,(a,b) in enumerate(zip([cu10]+cuns10,[cb10]+cn10)) if a!=b)
   assert (cf10==233 and cfns10==cn10)==(forward in [0x800,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e])
  else:assert ct10==cm10==0 and cf10==cu10==0xffffffff and cfns10==cuns10==[0xffffffff]*8 and forward==0x80032
 else:assert v[460:466]==[0,0,0,0xffffffff,0xffffffff,0] and v[466:490]==[0,0xffffffff,0xffffffff]*8
 cb7t,ct7t,ca7t,cf7t,cu7t,cm7t=v[490:496]
 cn7t=[v[496+3*i] for i in range(8)];cfns7t=[v[497+3*i] for i in range(8)];cuns7t=[v[498+3*i] for i in range(8)]
 assert ca7t in [0,1] and 0<=cm7t<512
 if forward in [0x800,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e]:
  assert ca7t==int([cb7t]+cn7t==[116,236,96,233,207,207,237,255,16])
  if ca7t:
   assert ct7t==116
   assert cm7t==sum(1<<i for i,(a,b) in enumerate(zip([cu7t]+cuns7t,[cb7t]+cn7t)) if a!=b)
   assert (cf7t==116 and cfns7t==cn7t)==(forward in [0x800,0x80036,0x80038,0x8003a,0x8003c,0x8003e])
  else:assert ct7t==cm7t==0 and cf7t==cu7t==0xffffffff and cfns7t==cuns7t==[0xffffffff]*8 and forward==0x80034
 else:assert v[490:496]==[0,0,0,0xffffffff,0xffffffff,0] and v[496:520]==[0,0xffffffff,0xffffffff]*8
 cb6,ct6,ca6,cf6,cu6,cm6=v[520:526]
 cn6=[v[526+3*i] for i in range(8)];cfns6=[v[527+3*i] for i in range(8)];cuns6=[v[528+3*i] for i in range(8)]
 assert ca6 in [0,1] and 0<=cm6<512
 if forward in [0x800,0x80036,0x80038,0x8003a,0x8003c,0x8003e]:
  assert ca6==int([cb6]+cn6==[236,116,96,233,207,207,237,255,16])
  if ca6:
   assert ct6==12
   assert cm6==sum(1<<i for i,(a,b) in enumerate(zip([cu6]+cuns6,[cb6]+cn6)) if a!=b)
   assert (cf6==12 and cfns6==cn6)==(forward in [0x800,0x80038,0x8003a,0x8003c,0x8003e])
  else:assert ct6==cm6==0 and cf6==cu6==0xffffffff and cfns6==cuns6==[0xffffffff]*8 and forward==0x80036
 else:assert v[520:526]==[0,0,0,0xffffffff,0xffffffff,0] and v[526:550]==[0,0xffffffff,0xffffffff]*8
 cb16,ct16,ca16,cf16,cu16,cm16=v[550:556]
 cn16=[v[556+3*i] for i in range(8)];cfns16=[v[557+3*i] for i in range(8)];cuns16=[v[558+3*i] for i in range(8)]
 assert ca16 in [0,1] and 0<=cm16<512
 if forward in [0x800,0x80038,0x8003a,0x8003c,0x8003e]:
  assert ca16==int([cb16]+cn16==[237,12,116,96,233,207,207,255,16])
  if ca16:
   assert ct16==140
   assert cm16==sum(1<<i for i,(a,b) in enumerate(zip([cu16]+cuns16,[cb16]+cn16)) if a!=b)
   assert (cf16==140 and cfns16==cn16)==(forward in [0x800,0x8003a,0x8003c,0x8003e])
  else:assert ct16==cm16==0 and cf16==cu16==0xffffffff and cfns16==cuns16==[0xffffffff]*8 and forward==0x80038
 else:assert v[550:556]==[0,0,0,0xffffffff,0xffffffff,0] and v[556:580]==[0,0xffffffff,0xffffffff]*8
 cb7d,ct7d,ca7d,cf7d,cu7d,cm7d=v[580:586]
 cn7d=[v[586+3*i] for i in range(8)];cfns7d=[v[587+3*i] for i in range(8)];cuns7d=[v[588+3*i] for i in range(8)]
 assert ca7d in [0,1] and 0<=cm7d<512
 if forward in [0x800,0x8003a,0x8003c,0x8003e]:
  assert ca7d==int([cb7d]+cn7d==[116,12,96,233,207,207,140,255,16])
  if ca7d:
   assert ct7d==54
   assert cm7d==sum(1<<i for i,(a,b) in enumerate(zip([cu7d]+cuns7d,[cb7d]+cn7d)) if a!=b)
   assert (cf7d==54 and cfns7d==cn7d)==(forward in [0x800,0x8003c,0x8003e])
  else:assert ct7d==cm7d==0 and cf7d==cu7d==0xffffffff and cfns7d==cuns7d==[0xffffffff]*8 and forward==0x8003a
 else:assert v[580:586]==[0,0,0,0xffffffff,0xffffffff,0] and v[586:610]==[0,0xffffffff,0xffffffff]*8
 cb12,ct12,ca12,cf12,cu12,cm12=v[610:616]
 cn12=[v[616+3*i] for i in range(8)];cfns12=[v[617+3*i] for i in range(8)];cuns12=[v[618+3*i] for i in range(8)]
 assert ca12 in [0,1] and 0<=cm12<512
 if forward in [0x800,0x8003c,0x8003e]:
  assert ca12==int([cb12]+cn12==[207,12,54,96,233,207,140,255,16])
  if ca12:
   assert ct12==223
   assert cm12==sum(1<<i for i,(a,b) in enumerate(zip([cu12]+cuns12,[cb12]+cn12)) if a!=b)
   assert (cf12==223 and cfns12==cn12)==(forward in [0x800,0x8003e])
  else:assert ct12==cm12==0 and cf12==cu12==0xffffffff and cfns12==cuns12==[0xffffffff]*8 and forward==0x8003c
 else:assert v[610:616]==[0,0,0,0xffffffff,0xffffffff,0] and v[616:640]==[0,0xffffffff,0xffffffff]*8
 cb9,ct9,ca9,cf9,cu9,cm9=v[640:646]
 cn9=[v[646+3*i] for i in range(8)];cfns9=[v[647+3*i] for i in range(8)];cuns9=[v[648+3*i] for i in range(8)]
 assert ca9 in [0,1] and 0<=cm9<512
 if forward in [0x800,0x8003e]:
  assert ca9==int([cb9]+cn9==[96,12,54,233,223,207,140,255,16])
  if ca9:
   assert ct9==64 and ct9==((cb9&0xdf)|(((480-1)>>4)&0x20))
   assert cm9==sum(1<<i for i,(a,b) in enumerate(zip([cu9]+cuns9,[cb9]+cn9)) if a!=b)
   assert (cf9==64 and cfns9==cn9)==(forward==0x800)
  else:assert ct9==cm9==0 and cf9==cu9==0xffffffff and cfns9==cuns9==[0xffffffff]*8 and forward==0x8003e
 else:assert v[640:646]==[0,0,0,0xffffffff,0xffffffff,0] and v[646:]==[0,0xffffffff,0xffffffff]*8
 assert c13attempt in [0,1] and um in [0,1,2,3]
 assert c19ba in [0,1] and tm in [0,1,2,3]
 assert c17ba in [0,1] and sm in [0,1]
 assert c2ba in [0,1] and rm in [0,1]
 assert c1attempt in [0,1] and fm in [0,1]
 assert c17attempt in [0,1] and dm in [0,1]
 assert c5battempt in [0,1] and nm in [0,1]
 assert c3attempt in [0,1] and em in [0,1]
 assert c2attempt in [0,1] and bm in [0,1]
 assert c0attempt in [0,1] and zm in [0,1]
 assert c5attempt in [0,1]
 assert c4attempt in [0,1] and 0<=cm<4
 assert forward in [0x800,0x8001,0x8002,0x8003,0x8004,0x8008,0x8009,0x800b,0x800d,0x800e,0x80010,0x80012,0x80014,0x80016,0x80018,0x8001a,0x8001c,0x8001e,0x80020,0x80022,0x80024,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e]
 assert enabled in [0,1] and 0<=mask<128
 # Validate the original prefix independently, retaining its exact full-byte checks.
 p=v[:76].copy();p[1]=0x800 if forward in [0x8009,0x800b,0x800d,0x800e,0x80010,0x80012,0x80014,0x80016,0x80018,0x8001a,0x8001c,0x8001e,0x80020,0x80022,0x80024,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e] else forward
 p[0]=p[1] if forward==0x8001 else 0x8006 if not v[28] else 0x8005 if forward!=0x8002 and v[30] else p[1]
 prefix=prefix_validate(p)
 if forward in [0x8001,0x8002]:
  assert attempted==count==mask==enabled==expected==observed==0
  assert first==0xffffffff and checked==restored==[0xffffffff]*7
  assert code==p[0]
 else:
  assert before==BASELINE
  assert mask==sum(1<<i for i,(a,b) in enumerate(zip(before,restored)) if a!=b)
  assert enabled==int(mask==0 and cm==0 and zm==0 and bm==0 and em==0 and nm==0 and dm==0 and fm==0 and rm==0 and sm==0 and tm==0 and um==0 and vm==0 and qm==0 and wm==0 and xm==0 and ym==0 and emsk==0 and vm2==0 and cm7==0 and cm10==0 and cm7t==0 and cm6==0 and cm16==0 and cm7d==0 and cm12==0 and cm9==0)
  assert code==(0x8006 if not v[28] else 0x8003f if cm9 else 0x8003d if cm12 else 0x8003b if cm7d else 0x80039 if cm16 else 0x80037 if cm6 else 0x80035 if cm7t else 0x80033 if cm10 else 0x80031 if cm7 else 0x8002f if vm2 else 0x8002d if emsk else 0x8002b if ym else 0x80029 if xm else 0x80027 if wm else 0x80025 if qm else 0x80023 if vm else 0x80021 if um else 0x8001f if tm else 0x8001d if sm else 0x8001b if rm else 0x80019 if fm else 0x80017 if dm else 0x80015 if nm else 0x80013 if em else 0x80011 if bm else 0x800f if zm else 0x800c if cm else 0x800a if mask else 0x8005 if v[30] else forward)
  if forward in [0x800,0x8009,0x800b,0x800d,0x800e,0x80010,0x80012,0x80014,0x80016,0x80018,0x8001a,0x8001c,0x8001e,0x80020,0x80022,0x80024,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e]:
   assert attempted==7
   if forward in [0x800,0x800b,0x800d,0x800e,0x80010,0x80012,0x80014,0x80016,0x80018,0x8001a,0x8001c,0x8001e,0x80020,0x80022,0x80024,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e]:
    assert count==7 and first==0xffffffff and checked==TARGET and expected==observed==0
   else:
    assert 0<=first<7 and count==first+1
    assert checked[:first]==TARGET[:first] and checked[first]!=TARGET[first]
    assert [expected,observed]==[TARGET[first],checked[first]]
    assert checked[first+1:]==[0xffffffff]*(6-first)
  else:
   assert attempted==count==expected==observed==0 and first==0xffffffff
   assert checked==[0xffffffff]*7
  if mask or cm or zm or bm or em or nm or dm or fm or rm or sm or tm or um or vm or qm or wm or xm or ym or emsk or vm2 or cm7 or cm10 or cm7t or cm6 or cm16 or cm7d or cm12 or cm9:assert v[18]==0x21 and v[30]&(1<<15)
 if forward in [0x8001,0x8002]:
  assert c4attempt==cm==0 and [c4check,c4restore,c5check,c5restore]==[0xffffffff]*4
  if forward==0x8001:assert c4==c5==0
 else:
  assert [c4,c5]==[0xa7,0x31]
  assert cm==int(c4restore!=c4)+2*int(c5restore!=c5)
  assert c4attempt==int(forward in [0x800,0x800b,0x800d,0x800e,0x80010,0x80012,0x80014,0x80016,0x80018,0x8001a,0x8001c,0x8001e,0x80020,0x80022,0x80024,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e])
  if c4attempt:
   assert c4check<=255 and c5check<=255
   assert (c4check==93 and c5check==c5)==(forward in [0x800,0x800d,0x800e,0x80010,0x80012,0x80014,0x80016,0x80018,0x8001a,0x8001c,0x8001e,0x80020,0x80022,0x80024,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e])
  else:assert c4check==c5check==0xffffffff
 assert c5attempt==int(forward in [0x800,0x800d,0x800e,0x80010,0x80012,0x80014,0x80016,0x80018,0x8001a,0x8001c,0x8001e,0x80020,0x80022,0x80024,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e])
 if c5attempt:
  assert c5target==((c5check&0xe0)|0x1e) and c5after<=255 and c4after<=255
  assert (c5after==c5target and c4after==93)==(forward in [0x800,0x800e,0x80010,0x80012,0x80014,0x80016,0x80018,0x8001a,0x8001c,0x8001e,0x80020,0x80022,0x80024,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e])
 else:assert c5target==0 and c5after==c4after==0xffffffff
 assert c0attempt==int(forward in [0x800,0x800e,0x80010,0x80012,0x80014,0x80016,0x80018,0x8001a,0x8001c,0x8001e,0x80020,0x80022,0x80024,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e])
 if forward in [0x8001,0x8002]:
  assert zm==0 and c0restore==0xffffffff
  if forward==0x8001:assert c0==0
 else:
  assert c0==0xc8 and zm==int(c0restore!=c0)
 if c0attempt:
  assert c0target==92 and c0after<=255 and c4after0<=255 and c5after0<=255
  assert (c0after==92 and c4after0==93 and c5after0==62)==(forward in [0x800,0x80010,0x80012,0x80014,0x80016,0x80018,0x8001a,0x8001c,0x8001e,0x80020,0x80022,0x80024,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e])
 else:assert c0target==0 and [c0after,c4after0,c5after0]==[0xffffffff]*3
 assert c2attempt==int(forward in [0x800,0x80010,0x80012,0x80014,0x80016,0x80018,0x8001a,0x8001c,0x8001e,0x80020,0x80022,0x80024,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e])
 if forward in [0x8001,0x8002]:
  assert bm==0 and c2restore==0xffffffff
  if forward==0x8001:assert c2==0
 else:assert c2==0x9f and bm==int(c2restore!=c2)
 if c2attempt:
  assert c2target==89 and all(n<=255 for n in [c2after,c0after2,c4after2,c5after2])
  assert (c2after==89 and c0after2==92 and c4after2==93 and c5after2==62)==(forward in [0x800,0x80012,0x80014,0x80016,0x80018,0x8001a,0x8001c,0x8001e,0x80020,0x80022,0x80024,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e])
 else:assert c2target==0 and [c2after,c0after2,c4after2,c5after2]==[0xffffffff]*4
 assert c3attempt==int(forward in [0x800,0x80012,0x80014,0x80016,0x80018,0x8001a,0x8001c,0x8001e,0x80020,0x80022,0x80024,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e])
 if forward in [0x8001,0x8002]:
  assert em==0 and c3restore==0xffffffff
  if forward==0x8001:assert c3==0
 else:assert c3==0x8c and em==int(c3restore!=c3)
 if c3attempt:
  assert c3target==((c3&0xe0)|((779//8-1)&31)) and all(n<=255 for n in [c3after,c0after3,c2after3,c4after3,c5after3])
  assert (c3after==c3target and c0after3==92 and c2after3==89 and c4after3==93 and c5after3==62)==(forward in [0x800,0x80014,0x80016,0x80018,0x8001a,0x8001c,0x8001e,0x80020,0x80022,0x80024,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e])
 else:assert c3target==0 and [c3after,c0after3,c2after3,c4after3,c5after3]==[0xffffffff]*5
 assert c5battempt==int(forward in [0x800,0x80014,0x80016,0x80018,0x8001a,0x8001c,0x8001e,0x80020,0x80022,0x80024,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e])
 if c5battempt:
  assert c5bbefore==c5after3==62 and c5btarget==((c5bbefore&127)|128)
  assert all(n<=255 for n in [c5bafter,c5bundo,c0afterb,c2afterb,c3afterb,c4afterb])
  assert nm==int(c5bundo!=c5bbefore)
  assert (c5bafter==190 and [c0afterb,c2afterb,c3afterb,c4afterb]==[92,89,128,93])==(forward in [0x800,0x80016,0x80018,0x8001a,0x8001c,0x8001e,0x80020,0x80022,0x80024,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e])
 else:assert v[143:153]==[0,0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
 if forward in [0x800,0x80016,0x80018,0x8001a,0x8001c,0x8001e,0x80020,0x80022,0x80024,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e]:
  assert c17<=255
  assert c17attempt==int(c17==v[69])
  if c17attempt:
   assert c17target==(c17&127) and all(n<=255 for n in [c17after,c17undo,c0after17,c2after17,c3after17,c4after17,c5after17])
   assert dm==int(c17undo!=c17)
   assert (c17after==c17target and [c0after17,c2after17,c3after17,c4after17,c5after17]==[92,89,128,93,190])==(forward in [0x800,0x80018,0x8001a,0x8001c,0x8001e,0x80020,0x80022,0x80024,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e])
  else:assert v[154:164]==[0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
 else:assert v[153:164]==[0,0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
 assert c1attempt==int(forward in [0x800,0x80018,0x8001a,0x8001c,0x8001e,0x80020,0x80022,0x80024,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e])
 if c1attempt:
  assert c1<=255 and c1target==89 and all(n<=255 for n in [c1after,c1undo,c0after1,c2after1,c3after1,c4after1,c5after1,c17after1])
  assert fm==int(c1undo!=c1)
  assert (c1after==89 and [c0after1,c2after1,c3after1,c4after1,c5after1,c17after1]==[92,89,128,93,190,99])==(forward in [0x800,0x8001a,0x8001c,0x8001e,0x80020,0x80022,0x80024,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e])
 else:assert v[164:176]==[0,0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
 if forward in [0x800,0x8001a,0x8001c,0x8001e,0x80020,0x80022,0x80024,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e]:
  assert c2bb<=255 and c2ba==int(c2bb==c2after1)
  if c2ba:
   assert c2bb==c2bt==89 and all(n<=255 for n in [c2bv,c2bu,c0after2b,c1after2b,c3after2b,c4after2b,c5after2b,c17after2b])
   assert rm==int(c2bu!=c2bb)
   assert (c2bv==89 and [c0after2b,c1after2b,c3after2b,c4after2b,c5after2b,c17after2b]==[92,89,128,93,190,99])==(forward in [0x800,0x8001c,0x8001e,0x80020,0x80022,0x80024,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e])
  else:assert v[177:188]==[0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
 else:assert v[176:188]==[0,0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
 if forward in [0x800,0x8001c,0x8001e,0x80020,0x80022,0x80024,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e]:
  assert c17bb<=255 and c17ba==int(c17bb==c17after2b)
  if c17ba:
   assert c17bb==99 and c17bt==((c17bb&127)|128) and all(n<=255 for n in [c17bv,c17bu,c0after17b,c1after17b,c2after17b,c3after17b,c4after17b,c5after17b])
   assert sm==int(c17bu!=c17bb)
   assert (c17bv==227 and [c0after17b,c1after17b,c2after17b,c3after17b,c4after17b,c5after17b]==[92,89,89,128,93,190])==(forward in [0x800,0x8001e,0x80020,0x80022,0x80024,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e])
  else:assert v[189:200]==[0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
 else:assert v[188:200]==[0,0,0,0xffffffff,0xffffffff,0,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff,0xffffffff]
 if forward in [0x800,0x8001e,0x80020,0x80022,0x80024,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e]:
  assert c19bb<=255 and c13b<=255 and c19ba==int(c19bb==v[70] and c13b==128)
  if c19ba:
   assert c19bb==16 and c19bt==((c19bb&31)|32) and all(n<=255 for n in [c19bv,c19bu,c13v,c17v,c0v,c1v,c2v,c3v,c4v,c5v,c13u])
   assert tm==int(c19bu!=c19bb)+2*int(c13u!=c13b)
   assert (c19bv==48 and [c13v,c17v,c0v,c1v,c2v,c3v,c4v,c5v]==[128,227,92,89,89,128,93,190])==(forward in [0x800,0x80020,0x80022,0x80024,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e])
  else:assert v[201:206]==[0,0,0xffffffff,0xffffffff,0] and v[207:216]==[0xffffffff]*9
 else:assert v[200:216]==[0,0,0,0xffffffff,0xffffffff,0,0]+[0xffffffff]*9
 if forward in [0x800,0x80020,0x80022,0x80024,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e]:
  assert c13before<=255 and c19before13<=255 and c13attempt==int(c13before==c13v and c19before13==c19bv)
  if c13attempt:
   assert c13before==128 and c19before13==48 and c13target==104
   assert all(n<=255 for n in [c13after,c13undo,c19after13,c17after13,c0after13,c1after13,c2after13,c3after13,c4after13,c5after13,c19undo13])
   assert um==int(c13undo!=c13before)+2*int(c19undo13!=c19before13)
   assert (c13after==104 and [c19after13,c17after13,c0after13,c1after13,c2after13,c3after13,c4after13,c5after13]==[48,227,92,89,89,128,93,190])==(forward in [0x800,0x80022,0x80024,0x80026,0x80028,0x8002a,0x8002c,0x8002e,0x80030,0x80032,0x80034,0x80036,0x80038,0x8003a,0x8003c,0x8003e])
  else:assert v[217:222]==[0,0,0xffffffff,0xffffffff,0] and v[223:232]==[0xffffffff]*9
 else:assert v[216:232]==[0,0,0,0xffffffff,0xffffffff,0,0]+[0xffffffff]*9
 return {'crtc_vblank_bit':{'before':cb9,'target':ct9,'attempted':ca9,'after':cf9,'restored':cu9,'cleanup_mask':cm9,'neighbors_before':cn9,'neighbors_after':cfns9,'neighbors_restored':cuns9},'crtc_vdisplay_low':{'before':cb12,'target':ct12,'attempted':ca12,'after':cf12,'restored':cu12,'cleanup_mask':cm12,'neighbors_before':cn12,'neighbors_after':cfns12,'neighbors_restored':cuns12},'crtc_vdisplay_high':{'before':cb7d,'target':ct7d,'attempted':ca7d,'after':cf7d,'restored':cu7d,'cleanup_mask':cm7d,'neighbors_before':cn7d,'neighbors_after':cfns7d,'neighbors_restored':cuns7d},'crtc_vblank_end':{'before':cb16,'target':ct16,'attempted':ca16,'after':cf16,'restored':cu16,'cleanup_mask':cm16,'neighbors_before':cn16,'neighbors_after':cfns16,'neighbors_restored':cuns16},'crtc_vtotal_low':{'before':cb6,'target':ct6,'attempted':ca6,'after':cf6,'restored':cu6,'cleanup_mask':cm6,'neighbors_before':cn6,'neighbors_after':cfns6,'neighbors_restored':cuns6},'crtc_vtotal_high':{'before':cb7t,'target':ct7t,'attempted':ca7t,'after':cf7t,'restored':cu7t,'cleanup_mask':cm7t,'neighbors_before':cn7t,'neighbors_after':cfns7t,'neighbors_restored':cuns7t},'crtc_vsync_low':{'before':cb10,'target':ct10,'attempted':ca10,'after':cf10,'restored':cu10,'cleanup_mask':cm10,'neighbors_before':cn10,'neighbors_after':cfns10,'neighbors_restored':cuns10},'crtc_vsync_high':{'before':cb7,'target':ct7,'attempted':ca7,'after':cf7,'restored':cu7,'cleanup_mask':cm7,'neighbors_before':cn7,'neighbors_after':cfns7,'neighbors_restored':cuns7},'vertical_valid_end':{'before':vb2,'target':vt2,'attempted':va2,'after':vf2,'restored':vu2,'cleanup_mask':vm2,'neighbors_before':vn2,'neighbors_after':vfns,'neighbors_restored':vuns},'vertical_sync_end':{'before':eb,'target':et,'attempted':ea,'after':ef,'restored':eu,'cleanup_mask':emsk,'neighbors_before':enb,'neighbors_after':ena,'neighbors_restored':enu},'vertical_sync_start':{'before':yb,'target':yt,'attempted':ya,'after':yf,'restored':yu,'cleanup_mask':ym,'neighbors_before':ynb,'neighbors_after':yna,'neighbors_restored':ynu},'vertical_valid_start':{'before':xb,'target':xt,'attempted':xa,'after':xf,'restored':xu,'cleanup_mask':xm,'neighbors_before':xnb,'neighbors_after':xna,'neighbors_restored':xnu,'same_value_drop_indistinguishable':True},'vertical_crtc':{'before':wb,'target':wt,'attempted':wa,'after':wf,'restored':wu,'cleanup_mask':wm,'neighbors_before':wnb,'neighbors_after':wna,'neighbors_restored':wnu},'vertical_total':{'before':qb,'target':qt,'attempted':qa,'after':qf,'restored':qu,'cleanup_mask':qm,'neighbors_before':qnb,'neighbors_after':qna,'neighbors_restored':qnu},'vertical_display_end':{'before':vb,'target':vt,'attempted':va,'after':vf,'restored':vu,'cleanup_mask':vm,'neighbors_before':nb,'neighbors_after':na,'neighbors_restored':nu},'cr13':{'before':c13before,'target':c13target,'attempted':c13attempt,'after':c13after,'restored':c13undo,'cleanup_mask':um,'CR19_before_after_recovered':[c19before13,c19after13,c19undo13],'neighbors_after':[c17after13,c0after13,c1after13,c2after13,c3after13,c4after13,c5after13]},'cr19_second':{'before':c19bb,'target':c19bt,'attempted':c19ba,'after':c19bv,'intermediate_restored':c19bu,'cleanup_mask':tm,'CR13_before_after_recovered':[c13b,c13v,c13u],'neighbors_after':[c17v,c0v,c1v,c2v,c3v,c4v,c5v]},'cr17_second':{'before':c17bb,'target':c17bt,'attempted':c17ba,'after':c17bv,'intermediate_restored':c17bu,'cleanup_mask':sm,'neighbors_after':[c0after17b,c1after17b,c2after17b,c3after17b,c4after17b,c5after17b]},'cr02_second':{'before':c2bb,'target':c2bt,'attempted':c2ba,'after':c2bv,'intermediate_restored':c2bu,'cleanup_mask':rm,'neighbors_after':[c0after2b,c1after2b,c3after2b,c4after2b,c5after2b,c17after2b],'same_value_write_observability':'dropped same-value write/undo cannot be distinguished by unchanged readback'},'cr01':{'before':c1,'target':c1target,'attempted':c1attempt,'after':c1after,'restored':c1undo,'cleanup_mask':fm,'neighbors_after':[c0after1,c2after1,c3after1,c4after1,c5after1,c17after1]},'cr17':{'before':c17,'target':c17target,'attempted':c17attempt,'after':c17after,'restored':c17undo,'cleanup_mask':dm,'CR00_after':c0after17,'CR02_after':c2after17,'CR03_after':c3after17,'CR04_after':c4after17,'CR05_after':c5after17},'cr05_second':{'before':c5bbefore,'target':c5btarget,'attempted':c5battempt,'after':c5bafter,'intermediate_restored':c5bundo,'cleanup_mask':nm,'CR00_after':c0afterb,'CR02_after':c2afterb,'CR03_after':c3afterb,'CR04_after':c4afterb},'cr03':{'before':c3,'target':c3target,'attempted':c3attempt,'after':c3after,'restored':c3restore,'cleanup_mask':em,'CR00_after':c0after3,'CR02_after':c2after3,'CR04_after':c4after3,'CR05_after':c5after3},'cr02':{'before':c2,'target':c2target,'attempted':c2attempt,'after':c2after,'restored':c2restore,'cleanup_mask':bm,'CR00_after':c0after2,'CR04_after':c4after2,'CR05_after':c5after2},'cr00':{'before':c0,'target':c0target,'attempted':c0attempt,'after':c0after,'restored':c0restore,'cleanup_mask':zm,'CR04_after':c4after0,'CR05_after':c5after0},'cr04':{'before':c4,'checked':c4check,'after_CR05':c4after,'restored':c4restore,'attempted':c4attempt,'target':93},'cr05':{'before':c5,'checked_before_write':c5check,'after':c5after,'restored':c5restore,'target':c5target,'attempted':c5attempt},'crtc_recovery_mask':cm,'code':code,'forward_status':forward,'prefix':prefix,
         'horizontal_before':before,'horizontal_checked':checked,'horizontal_restored':restored,
         'horizontal_checked_count':count,'horizontal_first_mismatch':None if first==0xffffffff else first,
         'horizontal_cleanup_mask':mask,'output_enable_attempted':bool(enabled),
         'CPU':v[11:14],'flags':v[8:11],'scope':'kernel horizontal prefix plus seven vertical words; not a visible mode switch'}
