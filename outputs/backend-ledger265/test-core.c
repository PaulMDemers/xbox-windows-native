/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <assert.h>
#include <string.h>
#include <stdio.h>
#include "ledger-core.h"
int main(void)
{
    unsigned tests=0;
    for (unsigned cache=0;cache<=512;cache++) for (unsigned units=0;units<=4;units++) {
        X265Binding b={42,cache+units,cache,units};
        assert((x265_account(&b,1)==0)==!!(cache+units));tests++;
        b.refs++;assert(x265_account(&b,1)!=0);tests++;
    }
    X265Binding pair[2]={{1,1,1,0},{2,4,0,4}};
    assert(!x265_account(pair,2));tests++;
    pair[1].identity=1;assert(x265_account(pair,2));tests++;
    pair[1].identity=0;assert(x265_account(pair,2));tests++;
    assert(x265_account(NULL,1));assert(x265_account(pair,517));tests+=2;
    uint64_t rows[2][8];memset(rows,0xa5,sizeof(rows));
    X265Rows out={rows,0,2,0};
    assert(x265_add(&out,1,2,3,4,5,6,7,8));tests++;
    assert(x265_add(&out,8,7,6,5,4,3,2,1));tests++;
    uint64_t saved[2][8];memcpy(saved,rows,sizeof(rows));
    for (unsigned i=0;i<10000;i++) {
        assert(!x265_add(&out,0,0,0,0,0,0,0,0));
        assert(out.count==2 && out.overflow && !memcmp(saved,rows,sizeof(rows)));tests++;
    }
    for(unsigned n=0;n<=X265_ROWS;n++) {
        unsigned pages=x265_page_count(n);
        assert((uint64_t)pages*X265_PAGE>=n);
        assert(!pages || (uint64_t)(pages-1)*X265_PAGE<n);tests++;
    }
    printf("PASS %u pure ledger checks; no renderer or native ownership exercised\n",tests);
    return 0;
}
