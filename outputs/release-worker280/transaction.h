/* New one-shot transaction; allocated fully before initial publication. */
typedef struct X280Transaction {
    X265State *pre,*post,*end;
    X279Proof release;
    unsigned state,candidate,old_halt,reason,armed,mutated_mask,post_captured,sealed;
    uint64_t finished;
    unsigned published[2];
    uint64_t records[2][16];
} X280Transaction;
