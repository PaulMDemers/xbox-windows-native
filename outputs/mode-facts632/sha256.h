/* SPDX-License-Identifier: MIT
 * Small bounded SHA-256 for read-only code identity, verified against hashlib.
 */
#ifndef SHA632_H
#define SHA632_H
#include <stdint.h>
#include <stddef.h>
static uint32_t rr632(uint32_t x,unsigned n){return (x>>n)|(x<<(32-n));}
static void sha632(const uint8_t *data,size_t size,uint8_t out[32]) {
 static const uint32_t k[64]={
 0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
 0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
 0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
 0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
 0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
 0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
 0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
 0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2};
 uint32_t h[8]={0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
 size_t blocks=(size+9+63)/64;
 for(size_t q=0;q<blocks;q++) {
  uint32_t w[64]={0};
  for(unsigned i=0;i<64;i++) {
   size_t p=q*64+i;uint8_t b=0;
   if(p<size)b=data[p];else if(p==size)b=0x80;
   else if(p>=blocks*64-8)b=(uint8_t)(((uint64_t)size*8)>>(8*(blocks*64-1-p)));
   w[i/4]|=(uint32_t)b<<(24-8*(i%4));
  }
  for(unsigned i=16;i<64;i++){uint32_t a=w[i-15],b=w[i-2];w[i]=w[i-16]+(rr632(a,7)^rr632(a,18)^(a>>3))+w[i-7]+(rr632(b,17)^rr632(b,19)^(b>>10));}
  uint32_t a=h[0],b=h[1],c=h[2],d=h[3],e=h[4],f=h[5],g=h[6],v=h[7];
  for(unsigned i=0;i<64;i++) {
   uint32_t t=v+(rr632(e,6)^rr632(e,11)^rr632(e,25))+((e&f)^(~e&g))+k[i]+w[i];
   uint32_t u=(rr632(a,2)^rr632(a,13)^rr632(a,22))+((a&b)^(a&c)^(b&c));
   v=g;g=f;f=e;e=d+t;d=c;c=b;b=a;a=t+u;
  }
  h[0]+=a;h[1]+=b;h[2]+=c;h[3]+=d;h[4]+=e;h[5]+=f;h[6]+=g;h[7]+=v;
 }
 for(unsigned i=0;i<32;i++)out[i]=(uint8_t)(h[i/4]>>(24-8*(i%4)));
}
#endif
