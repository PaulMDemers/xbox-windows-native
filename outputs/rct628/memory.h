/* MIT. Overflow-safe single-region read contract, shared with host controls. */
static int readable627(unsigned long address, unsigned long count,
 unsigned long base, unsigned long size, unsigned long state,
 unsigned long protect, int executable){
 unsigned long p=protect&255;
 if(!count||count>64||address>0xffffffffUL-count||base>0xffffffffUL-size)return 0;
 if(address<base||address-base>size||count>size-(address-base))return 0;
 if(state!=0x1000||(protect&0x100)||protect&~0x7ffUL)return 0;
 if(executable)return p==0x20||p==0x40||p==0x80;
 return p==2||p==4||p==8||p==0x20||p==0x40||p==0x80;
}
