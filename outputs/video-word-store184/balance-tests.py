"""Add explicit aligned fast-loop/tail coverage; retain preliminary host001."""
from pathlib import Path
k=Path(__file__).resolve().parent;assert not (k/'row-tests002.c').exists()
s=(k/'row-tests.c').read_text().replace('unsigned i,j,n,so,to,enabled,result;','unsigned i,j,n,so,to,enabled,result,at,fast=0,blocks=0,tails=0,small=0;')
marker='    free(s);free(d);free(expected);free(saved);';assert s.count(marker)==1
extra='''    {
        const unsigned lengths[]={0,4,8,12,28,32,36,60,64,68,124,128,256,1024,4096,7680,8192};
        /* LCG low bits correlate adjacent offsets; explicit Cartesian offsets
         * and both modes ensure fast block/tail cases cannot be missed. */
        for(at=0;at<sizeof(lengths)/sizeof(lengths[0]);at++)
        for(enabled=0;enabled<2;enabled++)for(so=64;so<68;so++)for(to=64;to<68;to++) {
            n=lengths[at];
            for(j=0;j<16448;j++)s[j]=(unsigned char)(j*37+at);
            memset(d,0x5a,16448);memcpy(expected,d,16448);memcpy(saved,s,16448);
            memmove(expected+to,s+so,n);result=XwCopyRow(d+to,s+so,n,enabled);
            CHECK(result==(unsigned)(enabled&&n&&so==64&&to==64));
            CHECK(memcmp(expected,d,16448)==0);CHECK(memcmp(saved,s,16448)==0);
            if(result){++fast;if(n>=32)++blocks;else ++small;if(n%32)++tails;}
        }
        CHECK(fast==16);CHECK(blocks==12);CHECK(small==4);CHECK(tails==8);
    }
'''
s=s.replace(marker,extra+marker).replace('16000 byte-oracle cases','16544 byte-oracle cases;explicit16fast/12block/8tail/4small')
(k/'row-tests002.c').write_bytes(s.encode())
s=(k/'host-tests.py').read_text().replace("dest=k/'host-tests.json'","dest=k/'host-tests002.json'").replace('/tmp/xwn-word184-recorded-tests','/tmp/xwn-word184-recorded-tests002').replace('row-tests.c','row-tests002.c').replace('44005','45641').replace('byte_oracle_cases=16000','byte_oracle_cases=16544').replace("k/'host-tests.py'","k/'host-tests002.py'")
(k/'host-tests002.py').write_bytes(s.encode())
p=k/'review-driver.py';s=p.read_text().replace("k/'host-tests.json'","k/'host-tests002.json'").replace('44005','45641');p.write_bytes(s.encode())
print('Explicit fast-loop coverage added in new002; host001 unchanged')
