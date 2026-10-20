/* MIT. Bounded observation, not a durability or successful reload claim. */
typedef struct { DWORD bytes; BYTE sha1[20]; } SAVED_SAMPLE;
static int saved_probe(SAVED_SAMPLE *sample,DWORD start);
static BOOL wait_saved_file(void){
 DWORD start=GetTickCount(),stable_start=start,first=0,valid=0,polls=0,i;
 SAVED_SAMPLE previous,current;int result;BOOL same;
 number("saved_wait_started",1);
 while(GetTickCount()-start<30000){
  polls++;result=saved_probe(&current,start);
  if(result<0){number("saved_wait_fatal",1);return FALSE;}
  if(GetTickCount()-start>=30000)break;
  if(result==1){
   if(!first){first=1;number("saved_first_readable_ms",GetTickCount()-start);}
   same=valid&&current.bytes==previous.bytes;
   if(same)for(i=0;i<20;i++)if(current.sha1[i]!=previous.sha1[i])same=FALSE;
   if(!same){valid=1;stable_start=GetTickCount();previous=current;}
   else valid++;
   if(valid>=3&&GetTickCount()-stable_start>=1000){
    for(i=0;i<20;i++)number("saved_sha1_byte",current.sha1[i]);
    number("saved_file_bytes",current.bytes);number("saved_equal_reads",valid);
    number("saved_stable_ms",GetTickCount()-stable_start);
    number("saved_wait_elapsed_ms",GetTickCount()-start);number("saved_wait_polls",polls);
    number("save_phase_file_observed",1);return TRUE;
   }
  }else valid=0;
  Sleep(250);
 }
 number("saved_wait_timeout",1);number("saved_wait_polls",polls);
 number("saved_wait_elapsed_ms",GetTickCount()-start);return FALSE;
}
