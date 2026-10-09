"""Read-only matching of an active outer call's token in the SAME process table."""
def find_close_scope(scopes, owner_process, handle):
    found=[s for s in scopes.values() if s['process']==owner_process and s['token_handle']==handle]
    if len(found)>1:raise ValueError('Ambiguous active token-close scope; never guess')
    return found[0] if found else None


def find_return_call(pending, thread, address, stack):
    calls=[c for c in pending.get((thread,address),[]) if stack==c['stack']+c['stack_delta']]
    if len(calls)>1:raise ValueError('Ambiguous return scope; never guess')
    return calls[0] if calls else None
