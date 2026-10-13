/*351 read-only eligible-plan accounting. Caller holds existing owner semaphore.
 * Original348 words0..7 and escape remain unchanged. Words8/9 are bytes;
 * word10 is a separate sticky351 error (1 overflow,2 invalid result/bytes).
 * No reset, functional admission, copy or fallback operation occurs here. */
static VOID XwnEligibleRecord(ULONG *stats,int result,ULONGLONG bytes)
{
 ULONGLONG old;
 if(result < -2 || result > 1 || (result == -1 && bytes) ||
    (result == 0 && bytes) || (result == 1 && !bytes)) {
  stats[10] |= 2; return;
 }
 if(result == -1) return;
 old=((ULONGLONG)stats[9]<<32)|stats[8];
 if(~(ULONGLONG)0-old < bytes) {old=~(ULONGLONG)0;stats[10]|=1;}
 else old+=bytes;
 stats[8]=(ULONG)old;stats[9]=(ULONG)(old>>32);
}
