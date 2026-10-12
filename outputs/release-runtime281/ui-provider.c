/* Acquire published UI capture; no UI lock/job or mutation is introduced. */
bool xwn_ui281_unbound(const uint64_t names[4],uint64_t *context)
{
    if(!qatomic_load_acquire(&frontend246_ready) || qatomic_load_acquire(&frontend246_state)!=2 ||
       ui265_error || ui265_rows.overflow || !ui265_rows.rows)return false;
    if(!x281_edges((const uint64_t (*)[8])ui265_rows.rows,ui265_rows.count,8,names))return false;
    unsigned holders=0,surfaces=0,native=0;uint64_t handle=0,window=0;
    for(unsigned i=0;i<ui265_rows.count;i++) {
        const uint64_t *r=ui265_rows.rows[i];
        if(r[0]==40){if(++holders!=1 || !r[1] || !r[2])return false;}
        if(r[0]==64){if(++surfaces!=1 || !r[1] || !r[2] || !r[4] || !r[5] || !r[6] || !r[7])return false;handle=r[6];window=r[7];}
    }
    for(unsigned i=0;i<ui265_rows.count;i++) {
        const uint64_t *r=ui265_rows.rows[i];
        if(r[0]==65){if(++native!=1 || r[1]!=handle || r[3]!=handle || r[2]!=window || r[4]!=window)return false;}
        if(r[0]==40 && r[2]!=handle)return false;
    }
    if(holders!=1 || surfaces!=1 || native!=1)return false;
    *context=handle;return true;
}
