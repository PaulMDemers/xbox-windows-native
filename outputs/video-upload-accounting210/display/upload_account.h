/* GPL-2.0-or-later. Bounded after-copy diagnostics; never owns a render lock. */
#ifndef XWN_UPLOAD_ACCOUNT_H
#define XWN_UPLOAD_ACCOUNT_H
#define XWA_KINDS 15
#define XWA_WORDS (8 + XWA_KINDS * 10)
typedef struct { ULONG boxes,fallbacks,overflow; ULONGLONG bytes; } XWA_COPY;
typedef struct {
 ULONG requests,explicit_rect,null_rect,boxes,fallbacks;
 ULONGLONG bytes,null_bytes;
} XWA_ROW;
typedef struct { ULONG errors,overflow; XWA_ROW row[XWA_KINDS]; } XWA_STATS;
static void XwaAdd32(ULONG *v,ULONG n,ULONG *overflow)
{
 if(n>~(ULONG)0-*v) {*v=~(ULONG)0;*overflow=1;} else *v+=n;
}
static void XwaAdd64(ULONGLONG *v,ULONGLONG n,ULONG *overflow)
{
 if(n>~(ULONGLONG)0-*v) {*v=~(ULONGLONG)0;*overflow=1;} else *v+=n;
}
static void XwaBox(XWA_COPY *c,ULONGLONG bytes)
{
#if XWN_UPLOAD_ACCOUNTING
 XwaAdd32(&c->boxes,1,&c->overflow);XwaAdd64(&c->bytes,bytes,&c->overflow);
#else
 (void)c;(void)bytes;
#endif
}
static void XwaFallback(XWA_COPY *c)
{
#if XWN_UPLOAD_ACCOUNTING
 XwaAdd32(&c->fallbacks,1,&c->overflow);
#else
 (void)c;
#endif
}
static void XwaRecord(XWA_STATS *s,ULONG kind,ULONG has_rect,const XWA_COPY *c)
{
#if XWN_UPLOAD_ACCOUNTING
 XWA_ROW *r;
 if(kind>=XWA_KINDS||has_rect>1){s->errors=1;return;}
 r=&s->row[kind];s->overflow|=c->overflow;
 XwaAdd32(&r->requests,1,&s->overflow);
 XwaAdd32(has_rect?&r->explicit_rect:&r->null_rect,1,&s->overflow);
 XwaAdd32(&r->boxes,c->boxes,&s->overflow);
 XwaAdd32(&r->fallbacks,c->fallbacks,&s->overflow);
 XwaAdd64(&r->bytes,c->bytes,&s->overflow);
 if(!has_rect)XwaAdd64(&r->null_bytes,c->bytes,&s->overflow);
#else
 (void)s;(void)kind;(void)has_rect;(void)c;
#endif
}
static void XwaSnapshot(const XWA_STATS *s,ULONG *out)
{
 ULONG i,a;const XWA_ROW *r;
 for(i=0;i<XWA_WORDS;i++)out[i]=0;
 out[0]=0x41555758;out[1]=119;out[2]=XWA_WORDS*4;
 out[3]=XWN_UPLOAD_ACCOUNTING;out[4]=XWA_KINDS;
 out[5]=s->errors;out[6]=s->overflow;
 for(i=0;i<XWA_KINDS;i++){
  r=&s->row[i];a=8+i*10;
  out[a]=r->requests;out[a+1]=r->explicit_rect;out[a+2]=r->null_rect;
  out[a+3]=r->boxes;out[a+4]=(ULONG)r->bytes;out[a+5]=(ULONG)(r->bytes>>32);
  out[a+6]=(ULONG)r->null_bytes;out[a+7]=(ULONG)(r->null_bytes>>32);
  out[a+8]=r->fallbacks;
 }
}
#endif
