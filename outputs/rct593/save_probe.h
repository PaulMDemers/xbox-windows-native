/* MIT. Exclusive against writers; read/hash the whole bounded file each time. */
static int saved_probe(SAVED_SAMPLE *sample,DWORD start){
 HANDLE file;HCRYPTPROV provider=0;HCRYPTHASH hash=0;
 DWORD error,high=0,size,total=0,n,hashbytes=20,afterhigh=0,after;static BYTE buffer[4096];int result=-1;
 file=CreateFileA(savepath,GENERIC_READ,FILE_SHARE_READ,0,OPEN_EXISTING,FILE_FLAG_SEQUENTIAL_SCAN,0);
 if(file==INVALID_HANDLE_VALUE){
  error=GetLastError();number("saved_probe_open_error",error);
  return error==ERROR_FILE_NOT_FOUND||error==ERROR_SHARING_VIOLATION||error==ERROR_LOCK_VIOLATION?0:-1;
 }
 SetLastError(0);size=GetFileSize(file,&high);error=GetLastError();
 if(error||high||size>=8*1024*1024){number("saved_probe_size_error",error);goto end;}
 if(size<=32){number("saved_probe_small_bytes",size);result=0;goto end;}
 if(!CryptAcquireContextA(&provider,0,0,PROV_RSA_FULL,CRYPT_VERIFYCONTEXT|CRYPT_SILENT)||
    !CryptCreateHash(provider,CALG_SHA1,0,0,&hash)){number("saved_probe_crypto_error",GetLastError());goto end;}
 while(total<size){
  if(GetTickCount()-start>=30000){result=0;goto end;}
  n=0;if(!ReadFile(file,buffer,(size-total)<sizeof(buffer)?size-total:sizeof(buffer),&n,0)){
   number("saved_probe_read_error",GetLastError());goto end;
  }
  if(!n){number("saved_probe_short_read",1);result=0;goto end;}
  if(!CryptHashData(hash,buffer,n,0)){number("saved_probe_hash_error",GetLastError());goto end;}
  total+=n;
 }
 n=0;if(!ReadFile(file,buffer,1,&n,0)){number("saved_probe_eof_error",GetLastError());goto end;}
 SetLastError(0);after=GetFileSize(file,&afterhigh);error=GetLastError();
 if(error){number("saved_probe_after_size_error",error);goto end;}
 if(n||after!=size||afterhigh){number("saved_probe_changed_during_read",1);result=0;goto end;}
 if(!CryptGetHashParam(hash,HP_HASHVAL,sample->sha1,&hashbytes,0)||hashbytes!=20){
  number("saved_probe_digest_error",GetLastError());goto end;
 }
 sample->bytes=size;result=1;
end:
 if(hash)CryptDestroyHash(hash);
 if(provider)CryptReleaseContext(provider,0);
 CloseHandle(file);return result;
}
