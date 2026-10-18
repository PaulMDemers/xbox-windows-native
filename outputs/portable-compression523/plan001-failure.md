# Preserved read-only plan001 failure

The streaming SHA helper returned a hash object instead of its hexadecimal digest.
Its comparison against historical hash strings refused the first file. No native
compression operation ran; no selected file was changed. Independent file_digest
readback confirmed all seven actual hashes match their own historical records.
Common002 changes only return h to return h.hexdigest(); plan002 uses that corrected
helper. Original plan001/common source/result are preserved. The previously
unexecuted apply001 now refers to plan002/common002 and remains one-shot.
