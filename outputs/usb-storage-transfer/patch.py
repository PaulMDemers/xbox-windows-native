"""Add bounded DMA/backend capture to an already exact candidate source copy."""
from pathlib import Path
import difflib

def apply(source, output):
    source=Path(source);output=Path(output);diff=[]
    names=['system/dma-helpers.c','block/block-backend.c']
    for name in names:
        p=source/name;old=p.read_text();s=old
        component='dma' if name.startswith('system/') else 'backend'
        s=s.replace('#include "qemu/osdep.h"','#include "qemu/osdep.h"\n#define XWN_TRANSFER_COMPONENT "'+component+'"\n#include "qemu/xwn-transfer.h"',1)
        if component=='dma':
            s=s.replace('    DMAIOFunc *io_func;','    uint64_t xwn_id;\n    DMAIOFunc *io_func;',1)
            s=s.replace('    trace_dma_complete(dbs, ret, dbs->common.cb);','    trace_dma_complete(dbs, ret, dbs->common.cb);\n    if (dbs->xwn_id) { xwn_transfer(dbs->xwn_id, 3, dbs->offset, 0, NULL, 0, dbs, ret, 0); }',1)
            s=s.replace('    dbs->acb = NULL;\n    dbs->offset += dbs->iov.size;', '''    if (dbs->xwn_id && dbs->iov.size) {
        xwn_transfer(dbs->xwn_id, 2, dbs->offset, dbs->iov.size,
                     &dbs->iov, 0, dbs, ret, 0);
    }
    dbs->acb = NULL;
    dbs->offset += dbs->iov.size;''',1)
            s=s.replace('    dbs->acb = dbs->io_func(dbs->offset, &dbs->iov,','''    if (dbs->xwn_id) {
        xwn_transfer(dbs->xwn_id, 1, dbs->offset, dbs->iov.size,
                     &dbs->iov, 0, dbs, 0, 0);
    }
    dbs->acb = dbs->io_func(dbs->offset, &dbs->iov,''',1)
            s=s.replace('    qemu_iovec_init(&dbs->iov, sg->nsg);','''    dbs->xwn_id = dir == DMA_DIRECTION_TO_DEVICE ?
        xwn_transfer(0, 0, offset, sg->size, NULL, 0, dbs, 0, sg->nsg) : 0;
    if (dbs->xwn_id) {
        for (int xwn_i = 0; xwn_i < sg->nsg; ++xwn_i) {
            xwn_transfer(dbs->xwn_id, 11, sg->sg[xwn_i].base,
                         sg->sg[xwn_i].len, NULL, 0, dbs, 0, xwn_i);
        }
    }
    qemu_iovec_init(&dbs->iov, sg->nsg);''',1)
        else:
            anchor='blk_co_do_pwritev_part(BlockBackend *blk,'
            at=s.index(anchor);end=s.index('\nint coroutine_fn blk_co_pwritev_part',at)
            body=s[at:end];body=body.replace('    int ret;','    int ret;\n    uint64_t xwn_id;',1)
            call='    ret = bdrv_co_pwritev_part(blk->root, offset, bytes, qiov, qiov_offset,\n                               flags);'
            assert call in body
            body=body.replace(call,'''    xwn_id = xwn_transfer(0, 4, offset, bytes, qiov, qiov_offset, blk, 0, flags);
'''+call+'''
    if (xwn_id) {
        xwn_transfer(xwn_id, 5, offset, bytes, qiov, qiov_offset, blk, ret, flags);
    }''')
            s=s[:at]+body+s[end:]
        assert s!=old
        p.write_text(s)
        diff.extend(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
    (source/'include/qemu/xwn-transfer.h').write_bytes((output/'xwn-transfer.h').read_bytes())
    (output/'transfer.patch').write_text(''.join(diff))
