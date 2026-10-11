/*263 Observation of the unchanged pending-work refusal, under existing locks. */
static unsigned x263_pending_mask(unsigned nop,unsigned flip,unsigned context,
                                 unsigned switching,unsigned flush,unsigned sync,
                                 unsigned downloads,unsigned dirty,unsigned shader)
{
    return (!!nop<<0)|(!!flip<<1)|(!!context<<2)|(!!switching<<3)|
           (!!flush<<4)|(!!sync<<5)|(!!downloads<<6)|(!!dirty<<7)|(!!shader<<8);
}
