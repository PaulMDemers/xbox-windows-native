/* SPDX-License-Identifier: MIT
 * Disposable NT5 fixture only. Synthetic keys/data, no existing key deletion.
 * CREATE_PHASE=1 creates; CREATE_PHASE=0 reopens on a later normal boot.
 * API-generated private state stays on the private guest disk.
 */
#define WINVER 0x0500
#define _WIN32_WINNT 0x0500
#include <windows.h>
#include <wincrypt.h>
#ifndef CREATE_PHASE
#error CREATE_PHASE required
#endif
static HANDLE log_file;
static const char *scope="probe";
static DWORD failures;
static BYTE blob_buffer[16384], signature[1024], public_blob[2048];
static BYTE token_data[1024], previous_sid[256];
static const BYTE plain[]="XWN423 synthetic persistence witness, not a secret";
static BYTE entropy_bytes[]={0x42,0x31,0x7a,0x19,0xe0,0x33,0x51,0x82};
static void zero(void *p,DWORD n){volatile BYTE *b=p;while(n--)*b++=0;}
static BOOL equal(const BYTE *a,const BYTE *b,DWORD n){while(n--)if(*a++!=*b++)return FALSE;return TRUE;}
static void number(const char *key,DWORD value){char line[192];DWORD n,w;n=wsprintfA(line,"%s.%s=%lu\r\n",scope,key,value);if(n>=sizeof(line)||!WriteFile(log_file,line,n,&w,0)||w!=n||!FlushFileBuffers(log_file))ExitProcess(90);}
static BOOL result(const char *key,BOOL ok){DWORD err=ok?0:GetLastError();number(key,err);if(!ok)failures++;return ok;}
static BOOL invariant(const char *key,BOOL ok){if(!ok)SetLastError(ERROR_INVALID_DATA);return result(key,ok);}
static BOOL save(const char *path,const BYTE *p,DWORD n){DWORD w=0,err;BOOL ok;HANDLE h=CreateFileA(path,GENERIC_WRITE,0,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,0);if(h==INVALID_HANDLE_VALUE)return FALSE;ok=WriteFile(h,p,n,&w,0)&&w==n&&FlushFileBuffers(h);err=GetLastError();CloseHandle(h);SetLastError(err);return ok;}
static BOOL load(const char *path,BYTE *p,DWORD *n){DWORD size,got=0,err;BOOL ok;HANDLE h=CreateFileA(path,GENERIC_READ,FILE_SHARE_READ,0,OPEN_EXISTING,0,0);if(h==INVALID_HANDLE_VALUE)return FALSE;size=GetFileSize(h,0);if(size==INVALID_FILE_SIZE||size>*n){CloseHandle(h);SetLastError(ERROR_INVALID_DATA);return FALSE;}ok=ReadFile(h,p,size,&got,0)&&got==size;err=GetLastError();CloseHandle(h);*n=got;SetLastError(err);return ok;}
static void rsa(BOOL machine){HCRYPTPROV provider=0;HCRYPTKEY key=0,imported=0;HCRYPTHASH hash=0;DWORD sn=sizeof(signature),pn=sizeof(public_blob);char pubpath[80],sigpath[80];DWORD flags=machine?CRYPT_MACHINE_KEYSET:0;
    scope=machine?"rsa_machine":"rsa_user";
    wsprintfA(pubpath,"C:\\XWN423\\%s.pub",scope);wsprintfA(sigpath,"C:\\XWN423\\%s.sig",scope);
    if(!result("acquire",CryptAcquireContextA(&provider,machine?"XWN423-machine-001":"XWN423-user-001",MS_ENHANCED_PROV_A,PROV_RSA_FULL,flags|(CREATE_PHASE?CRYPT_NEWKEYSET:0))))goto done;
    if(CREATE_PHASE){
        if(!result("generate",CryptGenKey(provider,AT_SIGNATURE,(1024UL<<16),&key)))goto done;
        if(!result("export_public",CryptExportKey(key,0,PUBLICKEYBLOB,0,public_blob,&pn)))goto done;
        if(!result("save_public",save(pubpath,public_blob,pn)))goto done;
    }else{
        if(!result("get_existing_key",CryptGetUserKey(provider,AT_SIGNATURE,&key)))goto done;
        if(!result("load_public",load(pubpath,public_blob,&pn)))goto done;
    }
    if(!result("import_public",CryptImportKey(provider,public_blob,pn,0,0,&imported)))goto done;
    if(!result("hash_create",CryptCreateHash(provider,CALG_SHA1,0,0,&hash)))goto done;
    if(!result("hash_data",CryptHashData(hash,plain,sizeof(plain),0)))goto done;
    if(CREATE_PHASE){
        if(!result("sign",CryptSignHashA(hash,AT_SIGNATURE,0,0,signature,&sn)))goto done;
        if(!result("save_signature",save(sigpath,signature,sn)))goto done;
    }else if(!result("load_signature",load(sigpath,signature,&sn)))goto done;
    if(!result("verify_persisted",CryptVerifySignatureA(hash,signature,sn,imported,0,0)))goto done;
    CryptDestroyHash(hash);hash=0;
    if(!result("fresh_hash_create",CryptCreateHash(provider,CALG_SHA1,0,0,&hash)))goto done;
    if(!result("fresh_hash_data",CryptHashData(hash,plain,sizeof(plain),0)))goto done;
    sn=sizeof(signature);
    if(!result("fresh_sign",CryptSignHashA(hash,AT_SIGNATURE,0,0,signature,&sn)))goto done;
    result("fresh_verify",CryptVerifySignatureA(hash,signature,sn,imported,0,0));
done:
    if(hash)CryptDestroyHash(hash);
    if(imported)CryptDestroyKey(imported);
    if(key)CryptDestroyKey(key);
    if(provider)CryptReleaseContext(provider,0);
}
static void dpapi(BOOL machine){DATA_BLOB in,out,entropy,decoded;DWORD n=sizeof(blob_buffer);char path[80];LPWSTR description=0;
    scope=machine?"dpapi_machine":"dpapi_user";wsprintfA(path,"C:\\XWN423\\%s.bin",scope);
    zero(&out,sizeof(out));zero(&decoded,sizeof(decoded));entropy.pbData=entropy_bytes;entropy.cbData=sizeof(entropy_bytes);
    if(CREATE_PHASE){
        in.pbData=(BYTE*)plain;in.cbData=sizeof(plain);
        if(!result("protect",CryptProtectData(&in,L"XWN423 synthetic",&entropy,0,0,CRYPTPROTECT_UI_FORBIDDEN|(machine?CRYPTPROTECT_LOCAL_MACHINE:0),&out)))goto done;
        if(!invariant("bounded_blob",out.cbData>0&&out.cbData<=sizeof(blob_buffer)))goto done;
        number("blob_bytes",out.cbData);
        if(!result("save_blob",save(path,out.pbData,out.cbData)))goto done;
        in=out;
    }else{
        if(!result("load_blob",load(path,blob_buffer,&n)))goto done;
        in.pbData=blob_buffer;in.cbData=n;number("blob_bytes",n);
    }
    if(!result("unprotect",CryptUnprotectData(&in,&description,&entropy,0,0,CRYPTPROTECT_UI_FORBIDDEN,&decoded)))goto done;
    invariant("exact_plaintext",decoded.cbData==sizeof(plain)&&equal(decoded.pbData,plain,sizeof(plain)));
done:
    if(description)LocalFree(description);
    if(decoded.pbData)LocalFree(decoded.pbData);
    if(out.pbData)LocalFree(out.pbData);
}
static void names(void){static const DWORD lengths[]={41,42,43,69};DWORD i,j,n,w;char path[100],label[40];BYTE value=0x6b;HANDLE h;
    scope="names";
    for(i=0;i<4;i++){
        n=wsprintfA(path,"C:\\XWN423\\");for(j=0;j<lengths[i];j++)path[n+j]=(char)('a'+j%26);path[n+lengths[i]]=0;
        h=CreateFileA(path,CREATE_PHASE?GENERIC_WRITE:GENERIC_READ,0,0,CREATE_PHASE?CREATE_NEW:OPEN_EXISTING,FILE_FLAG_WRITE_THROUGH,0);
        wsprintfA(label,"n%lu_open_error",lengths[i]);number(label,h==INVALID_HANDLE_VALUE?GetLastError():0);
        if(h!=INVALID_HANDLE_VALUE){BOOL ok;if(CREATE_PHASE)ok=WriteFile(h,&value,1,&w,0)&&w==1&&FlushFileBuffers(h);else{BYTE got=0;ok=ReadFile(h,&got,1,&w,0)&&w==1&&got==value;}wsprintfA(label,"n%lu_exact",lengths[i]);invariant(label,ok);CloseHandle(h);}
    }
}
static BOOL identity(void){HANDLE token;DWORD n=sizeof(token_data),sn=sizeof(previous_sid);TOKEN_USER *user=(TOKEN_USER*)token_data;BOOL ok;
    if(!result("token_open",OpenProcessToken(GetCurrentProcess(),TOKEN_QUERY,&token)))return FALSE;
    ok=GetTokenInformation(token,TokenUser,token_data,n,&n);{DWORD err=GetLastError();CloseHandle(token);SetLastError(err);}
    if(!result("token_user",ok)||!invariant("sid_valid",IsValidSid(user->User.Sid)))return FALSE;
    n=GetLengthSid(user->User.Sid);if(!invariant("sid_bounded",n>0&&n<=sizeof(previous_sid)))return FALSE;
    if(CREATE_PHASE)return result("sid_save",save("C:\\XWN423\\identity.bin",user->User.Sid,n));
    if(!result("sid_load",load("C:\\XWN423\\identity.bin",previous_sid,&sn)))return FALSE;
    return invariant("same_sid",sn==n&&equal(previous_sid,user->User.Sid,n));
}
void WINAPI mainCRTStartup(void){HCRYPTPROV memory=0;HANDLE token;TOKEN_PRIVILEGES tp;BOOL priv=FALSE;char fs[64];DWORD max_component=0,flags=0;
    if(CREATE_PHASE&&!CreateDirectoryA("C:\\XWN423",0))ExitProcess(91);
    log_file=CreateFileA(CREATE_PHASE?"C:\\XWN423\\create.log":"C:\\XWN423\\reopen.log",GENERIC_WRITE,FILE_SHARE_READ,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,0);if(log_file==INVALID_HANDLE_VALUE)ExitProcess(92);
    number("schema",423);number("create_phase",CREATE_PHASE);number("tick",GetTickCount());
    if(!identity()){CloseHandle(log_file);ExitProcess(93);}
    if(result("volume_info",GetVolumeInformationA("C:\\",0,0,0,&max_component,&flags,fs,sizeof(fs)))){number("max_component",max_component);number("filesystem_flags",flags);number("is_ntfs",lstrcmpiA(fs,"NTFS")==0);number("is_fatx",lstrcmpiA(fs,"FATX")==0);}
    if(result("memory_context",CryptAcquireContextA(&memory,0,MS_ENHANCED_PROV_A,PROV_RSA_FULL,CRYPT_VERIFYCONTEXT)))CryptReleaseContext(memory,0);
    names();rsa(FALSE);rsa(TRUE);dpapi(FALSE);dpapi(TRUE);
    scope="probe";number("api_failures",failures);number("complete",423);
    if(OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token)){
        zero(&tp,sizeof(tp));tp.PrivilegeCount=1;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED;
        if(LookupPrivilegeValueA(0,SE_SHUTDOWN_NAME,&tp.Privileges[0].Luid)){SetLastError(0);priv=AdjustTokenPrivileges(token,FALSE,&tp,0,0,0)&&GetLastError()==0;}CloseHandle(token);
    }
    number("restart_privilege",priv);number("restart_request",priv&&ExitWindowsEx(EWX_REBOOT,0));CloseHandle(log_file);ExitProcess(failures?1:0);
}
