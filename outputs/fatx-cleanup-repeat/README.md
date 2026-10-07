# Corrected wait-all repeat of cleanup0099

Cleanup-order001 completed500 iterations in each of three workers in16620ms.
Its exact cold worker files, zero API errors and no contended FATX resources
support removal of the reproduced cleanup cycle. It did not reboot because the
helper incorrectly treated a legal wait-all result2 as failure and intentionally
held for diagnosis. That historical run remains a failed shutdown qualification.

The Microsoft WaitForMultipleObjects contract accepts the full range0..nCount-1
when bWaitAll is true. This new sibling fixture keeps0099 and the workload
unchanged and corrects only that success predicate (0..2). The independent
pending-install check still requires WAIT_OBJECT_0 exactly. Expected counters,
zero errors, exact files, ordinary restart, event gates and cold audits remain
mandatory. See [the API/source record](waitall-correction.json).
