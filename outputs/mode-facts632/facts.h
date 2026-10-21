/* SPDX-License-Identifier: MIT
 * Read-only factual table extraction. All memory comes through a checked reader.
 * No display writes, no kernel patch, no full-image export.
 */
#include <stdint.h>
#include <string.h>
#include "sha256.h"
#include "known.h"
typedef int (*Reader632)(void *,uint32_t,void *,unsigned);
typedef struct {uint8_t crtc[35];uint32_t mmio[28];uint8_t encoder[14];} Profile632;
static uint32_t le632(const uint8_t *b){return (uint32_t)b[0]|((uint32_t)b[1]<<8)|((uint32_t)b[2]<<16)|((uint32_t)b[3]<<24);}
static int profile632(Reader632 read,void *o,uint32_t code,unsigned width,Profile632 *p) {
 uint8_t words[104],output[4];unsigned ci=(code>>8)&255,mi=(code>>16)&255,ei=code&15;
 if(!read(o,0x3410+34*ci,p->crtc,34) || !read(o,0x2c58+104*mi,words,104) ||
    !read(o,0x2c08+4*mi,output,4) || !read(o,0x3654+13*ei,p->encoder,13))return 0;
 unsigned pitch=width*4/8;
 p->crtc[19]=(uint8_t)pitch;p->crtc[25]|=(pitch>>3)&0xe0;p->crtc[29]|=(pitch>>6)&0x20;p->crtc[34]=0x83;
 for(unsigned i=0;i<26;i++)p->mmio[i]=le632(words+i*4);
 p->mmio[26]=le632(output);p->mmio[27]=0x100030;p->encoder[13]=0x28;return 1;
}
/* error1 version/export mismatch,2 read failure,3 PE identity,4 setter digest,
 * 5 table indices,6 known high profiles; output is untouched on any refusal. */
static int facts632(Reader632 read,void *o,unsigned major,unsigned minor,unsigned build,unsigned qfe,uint32_t av,Profile632 *out) {
 uint8_t header[4096],code[1181],digest[32],ci[34],mi[104],ei[13];Profile632 p[3];
 static const uint8_t expected_sha[32]={0x0f,0x8d,0xa8,0xf4,0x64,0xbe,0x4b,0x26,0xe3,0x2e,0x60,0xb7,0x76,0x54,0x84,0x89,0x8b,0x02,0x93,0x85,0x0d,0x8a,0x9f,0x39,0x96,0xca,0x44,0xa7,0x42,0x13,0x9c,0xcd};
 if(!read || !out || major!=1 || minor!=0 || build!=4034 || qfe!=1 || av!=0x8003130c)return 1;
 if(!read(o,0,header,sizeof(header)))return 2;
 unsigned pe=le632(header+0x3c);
 if(header[0]!='M' || header[1]!='Z' || pe>0xe00 || le632(header+pe)!=0x4550 ||
    header[pe+4]!=0x4c || header[pe+5]!=1 || header[pe+24]!=0x0b || header[pe+25]!=1 ||
    le632(header+pe+8)!=1004048809 || le632(header+pe+24+56)!=623712)return 3;
 if(!read(o,0x2130c,code,sizeof(code)))return 2;
 sha632(code,sizeof(code),digest);if(memcmp(digest,expected_sha,32))return 4;
 if(!read(o,0x3410,ci,34) || !read(o,0x2c58,mi,104) || !read(o,0x3654,ei,13))return 2;
 if(memcmp(ci,expected_ci,34) || memcmp(ei,expected_ei,13))return 5;
 for(unsigned i=0;i<26;i++)if(le632(mi+i*4)!=expected_mi[i])return 5;
 if(!profile632(read,o,0x880b0a02,1280,&p[0]) || !profile632(read,o,0x880e0c03,1920,&p[1]))return 2;
 if(memcmp(p[0].crtc,known_0_crtc,35) || memcmp(p[0].mmio,known_0_mmio,112) || memcmp(p[0].encoder,known_0_encoder,14) ||
    memcmp(p[1].crtc,known_1_crtc,35) || memcmp(p[1].mmio,known_1_mmio,112) || memcmp(p[1].encoder,known_1_encoder,14))return 6;
 if(!profile632(read,o,0x88080801,720,&p[2]))return 2;
 *out=p[2];return 0;
}
