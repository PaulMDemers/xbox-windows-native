/* MIT. Fixed 4+40 byte snapshot; no palettes, masks or pixel data reads. */
#ifndef DIB_HEADER604_H
#define DIB_HEADER604_H
typedef unsigned int DIBU;
typedef int (*DIBREAD)(void*,DIBU,void*,DIBU);
typedef struct {DIBU status,count,words[10],stride,bytes;} DIBSNAP;
/* Status:0 accepted;1 null;2 address wrap;3 unreadable;4 header size;
   5 dimensions;6 planes;7 bpp;8 compression;9 extent budget;10 sizeimage;
   11 palette count. These are observer policy, not GDI validity claims. */
static void dib_snapshot604(DIBREAD read,void*ctx,DIBU address,DIBSNAP*s) {
 DIBU i,w,h,bpp,planes,rows,bits,limit;
 s->status=0;s->count=0;s->stride=0;s->bytes=0;
 for(i=0;i<10;i++)s->words[i]=0;
 if(!address){s->status=1;return;}
 if(address>0xffffffffu-3u){s->status=2;return;}
 if(!read(ctx,address,s->words,4)){s->status=3;return;}
 s->count=1;
 if(s->words[0]!=40){s->status=4;return;}
 if(address>0xffffffffu-39u){s->status=2;return;}
 if(!read(ctx,address,s->words,40)){
  /* Failed callbacks may have copied a prefix. Retain only proven size. */
  for(i=1;i<10;i++)s->words[i]=0;
  s->words[0]=40;s->status=3;return;
 }
 s->count=10;
 if(s->words[0]!=40){s->status=4;return;}
 w=s->words[1];h=s->words[2];planes=s->words[3]&65535u;bpp=s->words[3]>>16;
 if(!w||(w&0x80000000u)||!h||h==0x80000000u){s->status=5;return;}
 if(planes!=1){s->status=6;return;}
 if(bpp!=1&&bpp!=4&&bpp!=8&&bpp!=16&&bpp!=24&&bpp!=32){s->status=7;return;}
 if(s->words[4]!=0){s->status=8;return;}
 rows=(h&0x80000000u)?0u-h:h;
 if(w>16384||rows>16384){s->status=9;return;}
 bits=w*bpp;s->stride=((bits+31)/32)*4;
 if(rows>67108864u/s->stride){s->status=9;return;}
 s->bytes=rows*s->stride;
 if(s->words[5]&&(s->words[5]<s->bytes||s->words[5]>67108864u)){s->status=10;return;}
 limit=bpp<=8?(1u<<bpp):256;
 if(s->words[8]>limit){s->status=11;return;}
}
#endif
