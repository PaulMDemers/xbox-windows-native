/* MIT. The subject keeps running. No suspension or acknowledgement-as-pause. */
static SNAP sample_subject[512],sample_tracer[512];
static BOOL window617(HANDLE subject,HANDLE recorder,HANDLE request,HANDLE ack,DWORD which,DWORD *count){
 SNAP a,b,ta,tb,oa,ob;DWORD n=0,j,wait,request_before=0,request_after=0,ack_tick=0;char line[160];
 if(!subject||!count||((recorder!=0)!=(request!=0))||((request!=0)!=(ack!=0)))return FALSE;
 zero(&ta,sizeof(ta));zero(&tb,sizeof(tb));
 if(!snap(GetCurrentProcess(),&oa,TRUE)||(recorder&&!snap(recorder,&ta,TRUE))||
    !snap(subject,&a,TRUE)||!mark("START",which,&a))return FALSE;
 if(request){
  request_before=GetTickCount();
  if(!SetEvent(request))return FALSE;
  request_after=GetTickCount();
 }
 do{
  wait=WaitForSingleObject(subject,100);
  if(wait!=WAIT_TIMEOUT||n>=512||!snap(subject,&sample_subject[n],TRUE)||
     (recorder&&!snap(recorder,&sample_tracer[n],TRUE)))return FALSE;
  if(ack&&!ack_tick){
   wait=WaitForSingleObject(ack,0);
   if(wait==WAIT_OBJECT_0)ack_tick=GetTickCount();
   else if(wait!=WAIT_TIMEOUT||GetTickCount()-a.tick>10000)return FALSE;
  }
  n++;
 }while((DWORD)(sample_subject[n-1].tick-a.tick)<20000);
 if(!snap(subject,&b,TRUE)||(recorder&&!snap(recorder,&tb,TRUE))||
    !snap(GetCurrentProcess(),&ob,TRUE)||!mark("END",which,&b))return FALSE;
 if(ack&&!ack_tick)return FALSE;
 if(!row("SUBJECT_START",which,0,&a)||!row("SUBJECT_END",which,0,&b)||
    !row("OBSERVER_START",which,0,&oa)||!row("OBSERVER_END",which,0,&ob))return FALSE;
 if(recorder&&(!row("TRACER_START",which,0,&ta)||!row("TRACER_END",which,0,&tb)))return FALSE;
 for(j=0;j<n;j++){
  if(!row("SUBJECT_SAMPLE",which,j,&sample_subject[j])||
     (recorder&&!row("TRACER_SAMPLE",which,j,&sample_tracer[j])))return FALSE;
 }
 wsprintfA(line,"WINDOW %lu %lu %lu %lu\r\n",which,request_before,request_after,ack_tick);
 *count=n;return text(line);
}
