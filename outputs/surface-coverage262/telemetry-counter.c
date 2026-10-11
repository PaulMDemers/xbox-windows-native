/*262 Saturating observation ticket. One overflow marker, no ownership changes.
 * Failed strong CAS means another thread advanced the monotone counter; at
 * most limit+1 advances exist. Never wraps and never resets during a run. */
static unsigned surface262_claim(unsigned *counter, unsigned limit)
{
    unsigned seen=qatomic_read(counter);
    while (seen<=limit) {
        unsigned actual=qatomic_cmpxchg(counter,seen,seen+1);
        if (actual==seen) return seen;
        seen=actual;
    }
    return limit+1;
}
