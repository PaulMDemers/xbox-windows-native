/* Independent guest expectation. The renderer must NOT call this generator. */
#ifndef X259_EXPECTED_H
#define X259_EXPECTED_H
#include <stdint.h>
static unsigned char x259_expected(uint32_t i,uint32_t mode)
{
    uint32_t seed=mode==3?1:0;
    unsigned char v=(unsigned char)((37*i+19*(i/16)+7*(i/256))^(83*seed));
    if(mode<3 && i>=4096 && i<4096+11*64){
        uint32_t row=(i-4096)/64,column=(i-4096)%64;
        if(column<13*4){
            uint32_t x=column/4;
            switch(column%4){
            case 0:v=(unsigned char)(17*x+29*row+3+31*mode);break;
            case 1:v=(unsigned char)(71*x+11*row+19+47*mode);break;
            case 2:v=(unsigned char)(5*x+97*row+101+67*mode);break;
            default:v=255;break;
            }
        }
    }
    return v;
}
#endif
