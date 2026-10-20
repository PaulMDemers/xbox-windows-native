/* MIT. Match RGB scenery before signaling the observer; captures stay private. */
#include "park_reference.h"
static BOOL park_verified;
static BOOL parkhash606(const BYTE *bits){
 HCRYPTPROV provider=0;HCRYPTHASH hash=0;BYTE row[460*3],digest[20];DWORD x,y,i,n=20;BOOL ok=FALSE;
 if(!CryptAcquireContextA(&provider,0,0,PROV_RSA_FULL,CRYPT_VERIFYCONTEXT))goto done;
 if(!CryptCreateHash(provider,CALG_SHA1,0,0,&hash))goto done;
 for(y=80;y<440;y++){
  for(x=160;x<620;x++){i=(x-160)*3;row[i]=bits[(y*640+x)*4+2];row[i+1]=bits[(y*640+x)*4+1];row[i+2]=bits[(y*640+x)*4];}
  if(!CryptHashData(hash,row,sizeof(row),0))goto done;
 }
 if(!CryptGetHashParam(hash,HP_HASHVAL,digest,&n,0)||n!=20)goto done;
 for(i=0;i<20;i++)if(digest[i]!=park_digest606[i])goto done;
 ok=TRUE;
done:
 if(hash)CryptDestroyHash(hash);
 if(provider)CryptReleaseContext(provider,0);
 return ok;
}
