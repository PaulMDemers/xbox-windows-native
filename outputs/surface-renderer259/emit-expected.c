#include <stdio.h>
#include "expected.h"
int main(void)
{
    for(unsigned mode=0;mode<4;mode++)
        for(unsigned i=0;i<16384;i++)
            if(putchar(x259_expected(i,mode))==EOF)return 1;
    return ferror(stdout)?2:0;
}
