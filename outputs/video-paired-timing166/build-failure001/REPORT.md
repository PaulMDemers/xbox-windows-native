The first compile failed on -Werror=misleading-indentation at runner.c16.
Source is preserved here. No binary or guest launch. Corrected only the line
break separating the guard and basename truncation; warning policy unchanged.

Initial import review then failed because the additional160 capture intentionally
does not contain ADVAPI32. Preserved review source; corrected review uses the
owned0.1.0 ADVAPI32 already used by the proven helper. Only new imports are from
the actual160 KERNEL32/USER32 capture. Provider paths/hashes are recorded.
