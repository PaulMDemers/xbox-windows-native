"""Extend the captured concurrency regression with metadata and enumeration workers."""
from pathlib import Path
k=Path(__file__).resolve().parent
source=(k.parent/'fatx-shutdown-concurrency/probe.c').read_text()
source=source.replace('Completed[3],Errors[3]','Completed[5],Errors[5]').replace('static BYTE Buffers[2][4097];','static BYTE Buffers[2][4097],Meta[4097];')
at=source.index('static DWORD WINAPI worker')
extra=r'''
static DWORD metadata_worker(void){
 DWORD i,j,n;HANDLE h;
 for(i=0;i<500;i++){
  for(j=0;j<sizeof(Meta);j++)Meta[j]=(BYTE)(j*19+i*31);
  h=CreateFileA("C:\\xwncc01\\meta.tmp",GENERIC_READ|GENERIC_WRITE,FILE_SHARE_READ|FILE_SHARE_WRITE|FILE_SHARE_DELETE,NULL,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,NULL);
  if(h==INVALID_HANDLE_VALUE){Errors[3]=(LONG)GetLastError();return 1;}
  if(!WriteFile(h,Meta,sizeof(Meta),&n,NULL)||n!=sizeof(Meta))Errors[3]=(LONG)(GetLastError()?GetLastError():ERROR_WRITE_FAULT);
  if(!Errors[3]&&(SetFilePointer(h,1025,NULL,FILE_BEGIN)!=1025||!SetEndOfFile(h)))Errors[3]=(LONG)(GetLastError()?GetLastError():ERROR_WRITE_FAULT);
  if(!Errors[3]&&(SetFilePointer(h,4097,NULL,FILE_BEGIN)!=4097||!SetEndOfFile(h)))Errors[3]=(LONG)(GetLastError()?GetLastError():ERROR_WRITE_FAULT);
  if(!Errors[3]&&(SetFilePointer(h,0,NULL,FILE_BEGIN)!=0||!WriteFile(h,Meta,sizeof(Meta),&n,NULL)||n!=sizeof(Meta)))Errors[3]=(LONG)(GetLastError()?GetLastError():ERROR_WRITE_FAULT);
  if(!Errors[3]&&!FlushFileBuffers(h))Errors[3]=(LONG)GetLastError();
  if(!CloseHandle(h)&&!Errors[3])Errors[3]=(LONG)GetLastError();
  if(Errors[3])return 1;
  if(!SetFileAttributesA("C:\\xwncc01\\meta.tmp",FILE_ATTRIBUTE_READONLY)||!SetFileAttributesA("C:\\xwncc01\\meta.tmp",FILE_ATTRIBUTE_ARCHIVE)||!MoveFileExA("C:\\xwncc01\\meta.tmp","C:\\xwncc01\\meta.bin",MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH)){Errors[3]=(LONG)GetLastError();return 1;}
  InterlockedIncrement(&Completed[3]);Sleep(1);
 }
 return 0;
}
static DWORD directory_worker(void){
 DWORD i,e;HANDLE h;WIN32_FIND_DATAA data;
 for(i=0;i<500;i++){
  h=FindFirstFileA("C:\\xwncc01\\*",&data);
  if(h==INVALID_HANDLE_VALUE){Errors[4]=(LONG)GetLastError();return 1;}
  while(FindNextFileA(h,&data)){}
  e=GetLastError();
  if(e!=ERROR_NO_MORE_FILES)Errors[4]=(LONG)(e?e:ERROR_INVALID_DATA);
  if(!FindClose(h)&&!Errors[4])Errors[4]=(LONG)GetLastError();
  if(Errors[4])return 1;
  InterlockedIncrement(&Completed[4]);Sleep(1);
 }
 return 0;
}
'''
source=source[:at]+extra+source[at:]
source=source.replace(' WaitForSingleObject(Start,INFINITE);',' WaitForSingleObject(Start,INFINITE);\n if(id==3)return metadata_worker();\n if(id==4)return directory_worker();')
source=source.replace('HANDLE threads[3]','HANDLE threads[5]').replace('i<3;i++','i<5;i++').replace('ATTEMPT_ONCE",3,500','ATTEMPT_ONCE",5,500').replace('WaitForMultipleObjects(3,threads,TRUE,180000)','WaitForMultipleObjects(5,threads,TRUE,600000)')
source=source.replace('report("ERRORS",Errors[0],Errors[1],Errors[2]);','report("ERRORS",Errors[0],Errors[1],Errors[2]);\n report("NAMESPACE_COUNTS",Completed[3],Completed[4],0);report("NAMESPACE_ERRORS",Errors[3],Errors[4],0);')
source=source.replace('if(Errors[0]||Errors[1]||Errors[2])','if(Errors[0]||Errors[1]||Errors[2]||Errors[3]||Errors[4])')
source=source.replace('if(status!=WAIT_OBJECT_0){report("HELD_FOR_DIAGNOSIS"','if(status>=WAIT_OBJECT_0+5){report("HELD_FOR_DIAGNOSIS"')
target=k/'probe.c';assert not (k/'probe-review.json').exists();target.write_text(source)
for name in ['Build.ps1','review.py','read-probe-symbols.py']:
    text=(k.parent/'fatx-shutdown-concurrency'/name).read_text()
    if name=='read-probe-symbols.py':text=text.replace('preferred_base=base,symbols=symbols','preferred_base=base,counter_count=5,symbols=symbols')
    (k/name).write_text(text)
