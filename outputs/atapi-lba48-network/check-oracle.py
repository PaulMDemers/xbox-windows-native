"""Reject missing shrink/check/overlap coverage and incomplete shutdown protocols."""
from common import *
def sample(mode):
    lines=[f'ATTEMPT_ONCE {mode} 11 4','INSTALL_IDLE_START 0 0 0','HIDSERV_START 4 0 0','NETWORK_START 32 131072 131072']
    for r in range(4):
        for i,p in enumerate(PREFIXES):
            lines += [f'CASE_COMPLETE {r} {i} {p+sum(CHUNKS)}',f'CASE_SHRINKS {r} {i} {shrinks(i)}',f'CASE_OVERLAP {r} {i} {mode}',f'CASE_DIRTY_OVERLAP {r} {i} {mode}']
    lines += [f'FLUSH_JOIN 0 {100 if mode else 0} 0',f'DIRTY_COVERAGE {44*mode} {44*mode} 0',f'COVERAGE 32 132 {44*mode}',f'COMPLETE {mode} 792 44','INSTALL_IDLE_END 0 0 0','HIDSERV_END 4 0 0','NETWORK_END 32 131072 131072','NORMAL_RESTART_REQUEST 0 0 0']
    return ('\r\n'.join(lines)+'\r\n').encode()
assert [shrinks(i) for i in range(11)]==[0,0,1,1,1,1,1,1,1,1,0]
assert sum(map(len,[expected(i) for i in range(11)]))>0
for mode in [0,1]:assert validate_log(mode,sample(mode))['passed']
bad={
 'network-short':sample(0).replace(b'NETWORK_START 32 131072 131072',b'NETWORK_START 31 126976 126976'),
 'network-missing':sample(0).replace(b'NETWORK_END 32 131072 131072\r\n',b''),
 'missing-case':sample(0).replace(b'CASE_COMPLETE 0 2 66925\r\n',b''),
 'no-shrink':sample(0).replace(b'CASE_SHRINKS 0 2 1',b'CASE_SHRINKS 0 2 0'),
 'failed-query':sample(0).replace(b'COMPLETE 0 792 44',b'FAIL_QUERY_SIZE 0 0 0'),
 'missing-overlap':sample(1).replace(b'CASE_OVERLAP 0 2 1',b'CASE_OVERLAP 0 2 0'),
 'missing-dirty-overlap':sample(1).replace(b'CASE_DIRTY_OVERLAP 0 2 1',b'CASE_DIRTY_OVERLAP 0 2 0'),
 'short-rendezvous':sample(1).replace(b'DIRTY_COVERAGE 44 44 0',b'DIRTY_COVERAGE 43 44 0'),
 'aborted-worker':sample(1)+b'ABORT_JOIN 258 100 0\r\n',
 'flush-timeout':sample(1).replace(b'FLUSH_JOIN 0 100 0',b'FLUSH_JOIN 258 100 0'),
 'short-checks':sample(1).replace(b'COVERAGE 32 132 44',b'COVERAGE 32 131 44'),
 'extra-failure':sample(1)+b'FAIL_RESTART 5 1 792\r\n',
 'missing-restart':sample(0).replace(b'NORMAL_RESTART_REQUEST 0 0 0\r\n',b''),
 'service-stopped':sample(0).replace(b'HIDSERV_START 4 0 0',b'HIDSERV_START 1 2 0'),
 'service-failed-late':sample(0).replace(b'HIDSERV_END 4 0 0',b'HIDSERV_END 1 0 0'),
}
results={name:not validate_log(1 if name in ['missing-overlap','missing-dirty-overlap','short-rendezvous','aborted-worker','flush-timeout','short-checks','extra-failure'] else 0,data)['passed'] for name,data in bad.items()}
assert all(results.values()),results
events=[]
for i,p in enumerate(PREFIXES):
    old=p
    for j,chunk in enumerate(CHUNKS):
        end=old+chunk;events.append(dict(index=i,append=j,old=old,new=end,mapping_max=end+35,allocation_mapped=((end+35+65535)//65536)*65536,allocation_final=((end+65535)//65536)*65536,shrinks=((end+35+65535)//65536>(end+65535)//65536)));old=end
save(k/'oracle-review.json',dict(validator_negative_checks=results,expected_appends=792,expected_reopens=132,expected_allocation_shrinks=32,helper_sha256=read(k/'build-review.json')['probe_sha256'],events=events,limits='Synthetic oracle checks, not guest execution. Allocation shrink is observed via NtQueryInformationFile; intermediate FAT chains are not captured. Final chains and bytes require independent cold audit.'))
print('Oracle requires running service at start/end and mapped workload; all13 negative checks rejected')
