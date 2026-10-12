/* Complete captured known graph, with only the declared unit/ref changes. */
static bool x280_retained(X265State *a,X265State *b,unsigned candidate)
{
    if(a->ledger.overflow || b->ledger.overflow)return false;
    unsigned ia=0,ib=0;
    while(ia<a->ledger.count || ib<b->ledger.count) {
        while(ia<a->ledger.count && (a->ledger.rows[ia][0]==17 || a->ledger.rows[ia][0]>=64))ia++;
        while(ib<b->ledger.count && (b->ledger.rows[ib][0]==17 || b->ledger.rows[ib][0]>=64))ib++;
        if(ia==a->ledger.count || ib==b->ledger.count)return ia==a->ledger.count&&ib==b->ledger.count;
        uint64_t expected[8];memcpy(expected,a->ledger.rows[ia++],sizeof(expected));
        if(candidate) {
            if(expected[0]==3) {
                if(expected[1]>=4 || expected[2]!=a->proof278.textures[expected[1]].identity || expected[3])return false;
                expected[2]=0;expected[4]=1;
            } else if(expected[0]==4 || expected[0]==5) {
                for(unsigned i=0;i<4;i++)if(expected[1]==a->proof278.textures[i].identity) {
                    if(expected[2]!=2)return false;
                    expected[2]=1;
                    if(expected[0]==5){if(expected[3]!=1 || expected[4]!=1)return false;expected[4]=0;}
                }
            }
        }
        if(memcmp(expected,b->ledger.rows[ib++],sizeof(expected)))return false;
    }
    return true;
}
