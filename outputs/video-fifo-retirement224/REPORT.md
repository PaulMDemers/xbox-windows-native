# Native bounded FIFO observation224

Both fresh ordinary OFF/ON cases passed the bounded observation/CPU lifetime
and cold integrity scope. This checkpoint grants no GPU ownership or submission.
The active physical system and0101/video0093/0088 rollback/immutable0.1.0 remain
unchanged. No physical FTP, device branch integration or debugger was used.

## control001

Accepted 2026-10-10T18:07:05.313841+00:00; dashboard returned 2026-10-10T18:08:28.058616+00:00;
closed 2026-10-10T18:08:48.475111+00:00.

Raw observation: 0 reads; reasons UNMODELED_BUSY, NO_OWNERSHIP.
CPU:65 allocations/releases/exposure refusals,3194880 checked bytes,four joined workers.
Cold allocation:320 directories/6724 files/
321 directory clusters;zero errors/orphans. Five hives and
28 protected file hashes passed. One normal shutdown; no new application events.
Strict whole-boot qualification:False. Actual warnings/errors:
```json
[
  {
    "offset": 35520,
    "record": 204,
    "generated_unix": 1791670038,
    "written_unix": 1791670068,
    "event_id_hex": "c0040031",
    "event_id": 49,
    "type": 1,
    "source": "Ftdisk",
    "computer": "XWN-PC",
    "strings": [
      "\\Device\\HarddiskVolume6"
    ],
    "data_hex": "000000000100560000000000310004c0030000000000000000000000000000000000000000000000"
  }
]
```

## candidate001

Accepted 2026-10-10T18:09:53.138139+00:00; dashboard returned 2026-10-10T18:11:23.293740+00:00;
closed 2026-10-10T18:11:43.183291+00:00.

Raw observation: 128 reads; reasons UNMODELED_BUSY, NO_OWNERSHIP.
CPU:65 allocations/releases/exposure refusals,3194880 checked bytes,four joined workers.
Cold allocation:320 directories/6724 files/
321 directory clusters;zero errors/orphans. Five hives and
28 protected file hashes passed. One normal shutdown; no new application events.
Strict whole-boot qualification:False. Actual warnings/errors:
```json
[
  {
    "offset": 35520,
    "record": 204,
    "generated_unix": 1791670206,
    "written_unix": 1791670236,
    "event_id_hex": "c0040031",
    "event_id": 49,
    "type": 1,
    "source": "Ftdisk",
    "computer": "XWN-PC",
    "strings": [
      "\\Device\\HarddiskVolume6"
    ],
    "data_hex": "000000000100560000000000310004c0030000000000000000000000000000000000000000000000"
  }
]
```

First sequential round (all eight rounds retained in audit/raw log):

| Register | Offset | Value |
|---|---:|---:|
| NV_PFIFO_CACHE1_PUSH0 | `0x003200` | `0x00000000` |
| NV_PFIFO_CACHE1_PUSH1 | `0x003204` | `0x00000001` |
| NV_PFIFO_CACHE1_PUT | `0x003210` | `0x00000000` |
| NV_PFIFO_CACHE1_STATUS | `0x003214` | `0x00000010` |
| NV_PFIFO_CACHE1_DMA_PUSH | `0x003220` | `0x00000000` |
| NV_PFIFO_CACHE1_DMA_STATE | `0x003228` | `0x00000000` |
| NV_PFIFO_CACHE1_DMA_SUBROUTINE | `0x00324c` | `0x00000000` |
| NV_PFIFO_CACHE1_DMA_PUT | `0x003240` | `0x00000000` |
| NV_PFIFO_CACHE1_DMA_GET | `0x003244` | `0x00000000` |
| NV_PFIFO_CACHE1_PULL0 | `0x003250` | `0x00000000` |
| NV_PFIFO_CACHE1_GET | `0x003270` | `0x00000000` |
| NV_PFIFO_RUNOUT_STATUS | `0x002400` | `0x00000010` |
| NV_PFIFO_INTR_0 | `0x002100` | `0x00000000` |
| NV_PGRAPH_INTR | `0x400100` | `0x00000000` |
| NV_PGRAPH_CTX_CONTROL | `0x400144` | `0x10000100` |
| NV_PGRAPH_CTX_USER | `0x400148` | `0x00000001` |

## Evidence and limits

Independent [state review](state-review.json) decodes all eight identical rounds:
PFIFO channel 1, PGRAPH channel 0, current context invalid, cache push/pull and
DMA push disabled, zero DMA pointers and IRQs. The pinned model requires a valid
matching context for its context-switch path. Inferring that a new submission
would need context service is separate from an observed context-switch request;
224 issued none. Hardware switching mode is outside these sampled words.

Independent pair-review.json verified110 frozen inputs, exact actual logs,
source derivation and retained001 inputs. Shared context/sampler objects link both
drivers. Actual compiled16-word tables and intended NT5 provider exports passed.
ASan/UBSan host substitutes executed actual driver dispatch/cleanup, both modes,
mapping failure cleanup, wrong-owner/stale/reserved/short/elevated/lock rejection.
Sampler tests covered65536 DMA-state patterns and128 interrupted read positions;
nineteen parser checks reject malformed/reordered/incomplete/misdecoded evidence.

Build001 strict-aliasing failure is preserved with every exact input. Corrected
host test uses memcpy without disabling warnings; no native source changed.
Initial import review misclassified READ_REGISTER_ULONG as a HAL export. Actual
kernel export/provider pins corrected that assertion; failed script is retained.
The original inventory predates moving the table from header to C; its exact
failed-build source is retained. model-review002 checks final source/native bytes.

Eight immediate non-atomic sequential snapshots cannot prove producer/backend
retirement. The pinned model does not maintain DMA busy, returns constant empty
RUNOUT_STATUS and does not implement real PGRAPH_STATUS. NO_OWNERSHIP and
UNMODELED_BUSY remain mandatory even if register pointers/counts appear quiet.
OBSERVED means bounded reads completed. CPU EXPOSE still HOLD. No GPU writes,
RAMIN/USER mappings, descriptors, firmware channel borrow or reset were added.
Successful read mappings remain resident until reboot. Native fallback fault
cleanup, runtime PTE/cache aliases, backend drain and physical acceleration are
unqualified. Cold checks cover full allocation and selected protected contents,
not every payload byte. No event gate was weakened.

Private seeds:E:/Codex-archive/xbox-windows-native/retirement224.
Closed runs:E:/Codex-private-artifacts/xbox-windows-feasibility/retirement224-runs.
ALL root-owned224 processes closed; no old launch/collection/audit is repeated.
20GiB build guard remains unchanged; backing chains were not moved.
