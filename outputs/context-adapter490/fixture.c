/* SPDX-License-Identifier: MIT
 * Actual privileged adapter/capture execution; kernel IO and allocations modeled.
 */
typedef unsigned int u32;
typedef unsigned char u8;
#define API __attribute__((stdcall))
static void emit(u8 v){__asm__ volatile("outb %0,$0xe9"::"a"(v));}
static void bytes(const void*p,u32 n){const u8*b=p;for(u32 i=0;i<n;i++)emit(b[i]);}
static void fail(u32 line){emit('F');bytes(&line,4);__asm__ volatile("outl %0,$0xf4"::"a"(0x11));for(;;)__asm__ volatile("cli;hlt");}
#define CHECK(x) do{if(!(x))fail(__LINE__);}while(0)
static void zero(void*p,u32 n){u8*b=p;for(u32 i=0;i<n;i++)b[i]=0;}
static void copy(void*d,const void*s,u32 n){u8*a=d;const u8*b=s;for(u32 i=0;i<n;i++)a[i]=b[i];}
static int equal(const void*a,const void*b,u32 n){const u8*x=a,*y=b;for(u32 i=0;i<n;i++)if(x[i]!=y[i])return 0;return 1;}
static void context(u32 cr2,u32 cr3){__asm__ volatile("mov %0,%%cr2;mov %1,%%cr3"::"r"(cr2),"r"(cr3):"memory");}
extern void test_enter(void),fixture_success(void);
extern u8 context490_packet[400],context490_first[160],context490_second[160],witness_record[256],blentry[1024];
extern u32 context490_claim;
u32 fixture_saved_stack,fixture_flags,expected_frame[9],actual_frame[9],outcome;
u32 diag_closed,diag_handle,diag_reason,diag_iosb[2],diag_record[44],before_marker_record[24];
u32 kernelram,bootloaderram,phys_bootloaderram,phys_kernelram,cromwellsize;
u8 kernel[256],kernel_copy[256],high_loader[1024],low_loader[1024];
static u8 pristine[400],first[160],written[400];
static u32 mode,target,step,capbytes,calls[2][4],case_count;
static u32 which(u32 h){CHECK(h==0x4901 || h==0x4902);return h-0x4901;}
static void io_step(u32 file,u32 operation){
    CHECK(file<2 && operation<4);calls[file][operation]++;
    CHECK(calls[file][operation]==1);
    CHECK(step==file*4+operation);step++;
    if(file==0)CHECK(context490_claim==1 && *(u32*)(context490_first+132)==1 && !*(u32*)(context490_second+132));
    else CHECK(context490_claim==2 && *(u32*)(context490_second+132)==1 && equal(first,context490_first,160));
}
static u32 API create(u32*h,u32 access,u32*oa,u32*iosb,u32 alloc,u32 attrs,u32 share,u32 disposition,u32 options){
    u32 file=step/4;io_step(file,0);
    CHECK(access==0x40100000 && !alloc && attrs==0x80 && !share && disposition==2 && options==0x62);
    CHECK(oa[0]==0 && oa[2]==0x40);u8*name=(u8*)oa[1];u32 len=*(unsigned short*)name;
    CHECK(*(unsigned short*)(name+2)==len+1);u8*path=*(u8**)(name+4);
    const char*expect=file?"\\Device\\Harddisk0\\Partition1\\Applications\\XWNBoot490a\\context.bin":"\\Device\\Harddisk0\\Partition1\\Applications\\XWNBoot490a\\handoff.bin";
    u32 n=0;while(expect[n])n++;CHECK(n==len && equal(path,expect,n+1));
    if(!file)copy(first,context490_first,160);
    if(file==target && mode==1)return 0xc0000035;
    if(file==target && mode==2)return 0x103;
    *h=file==target && mode==6?0:0x4901+file;
    if(file==target && mode==4)return 0;
    iosb[0]=file==target && mode==3?0xc0000185:0;iosb[1]=file==target && mode==5?1:2;
    return 0;
}
static u32 API write_file(u32 h,u32 event,u32 apc,u32 ctx,u32*iosb,const void*buf,u32 n,u32 offset){
    u32 file=which(h);io_step(file,1);CHECK(!event && !apc && !ctx && !offset && n==(file?400u:256u));
    CHECK(buf==(file?(void*)context490_packet:(void*)witness_record));
    if(file==target && mode==7)return 0xc0000185;
    u32 actual=n-(file==target && mode==11);
    if(file){copy(written,buf,actual);capbytes=actual;}
    if(file==target && mode==10)return 0;
    iosb[0]=file==target && mode==9?0xc0000185:0;iosb[1]=file==target && mode==12?n+1:actual;
    return file==target && mode==8?0x103:0;
}
static u32 API flush(u32 h,u32*iosb){
    u32 file=which(h);io_step(file,2);
    if(file==target && mode==16)return 0;
    iosb[0]=file==target && mode==15?0xc0000185:0;iosb[1]=0;
    return file==target && mode==13?0xc0000185:file==target && mode==14?0x103:0;
}
static u32 API close_file(u32 h){
    u32 file=which(h);io_step(file,3);
    if(file==target && mode==17)return 0xc0000185;
    if(file==target && mode==18)return 0x103;
    if(!file){context(0x6789a000,0x1002000);if(mode==24)context490_claim=0;if(mode==25)*(u32*)(context490_second+132)=1;if(mode==26)context490_second[0]^=1;}
    if(file && mode==19)kernel_copy[12]^=1;
    if(file && mode==20)high_loader[500]^=1;
    if(file && mode==21)low_loader[500]^=1;
    return 0;
}
void *DiagNtCreateFile=create,*DiagNtWriteFile=write_file,*DiagNtFlushBuffersFile=flush,*DiagNtClose=close_file;
static void run(u32 m,u32 t){
    mode=m;target=t;step=capbytes=0;zero(calls,sizeof calls);zero(written,sizeof written);zero(actual_frame,sizeof actual_frame);
    copy(context490_packet,pristine,400);context490_claim=0;diag_closed=2;diag_handle=0;diag_reason=0;zero(diag_iosb,8);zero(witness_record+16,224);
    diag_record[5]=6;diag_record[30]=diag_record[31]=1;context(0x12345000,0x1000000);
    for(u32 i=0;i<256;i++)kernel[i]=(u8)(i*19+7);
    copy(kernel_copy,kernel,256);copy(high_loader,blentry,1024);copy(low_loader,blentry,1024);
    *(u32*)(high_loader+74)=phys_bootloaderram+80;*(u32*)(low_loader+74)=phys_bootloaderram+80;
    if(m==22)context490_claim=1;
    if(m==23)context490_first[0]^=1;
    fixture_flags=t?0x682:0x282;outcome=99;test_enter();
    if(m==0){
        CHECK(outcome==1 && step==8 && capbytes==400 && diag_closed==2 && equal(expected_frame,actual_frame,36));
        CHECK(equal(witness_record+160,expected_frame,36));CHECK(equal(first,context490_first,160));
        CHECK(*(u32*)(written+24)==2 && *(u32*)(written+36)==expected_frame[3]-32);
        CHECK(*(u32*)(written+64+28)==0x12345000 && *(u32*)(written+224+28)==0x6789a000);
        CHECK(*(u32*)(written+64+32)==0x1000000 && *(u32*)(written+224+32)==0x1002000);
        CHECK((*(u32*)(written+64+20)&0x602)==(fixture_flags&0x602));
        emit('S');bytes(&t,4);bytes(written,400);bytes(expected_frame,36);bytes(actual_frame,36);
    }else{
        u32 reason=m<=6?(t?22:13):m<=12?(t?23:14):m<=16?(t?24:15):m<=18?(t?25:16):m<=21?m-2:m<=23?20:21;
        CHECK(outcome==0 && diag_reason==reason);
        if(m<=18){u32 op=m<=6?0:m<=12?1:m<=16?2:3;CHECK(step==t*4+op+1);}
        if(m==22 || m==23)CHECK(step==0 && !capbytes);
        if(m>=24)CHECK(step==4 && !capbytes);
        if(m>=19 && m<=21)CHECK(step==8 && capbytes==400 && diag_closed==2);
        emit('R');bytes(&m,4);bytes(&t,4);bytes(&reason,4);bytes(&step,4);bytes(&capbytes,4);
    }
    case_count++;
}
void test_main(void){
    kernelram=(u32)kernel_copy;bootloaderram=(u32)high_loader;phys_bootloaderram=(u32)low_loader;phys_kernelram=(u32)kernel_copy;cromwellsize=256;
    copy(pristine,context490_packet,400);bytes("T490",4);
    for(u32 t=0;t<2;t++){run(0,t);for(u32 m=1;m<=18;m++)run(m,t);}
    for(u32 m=19;m<=26;m++)run(m,1);
    CHECK(case_count==46);emit('P');bytes(&case_count,4);
}
