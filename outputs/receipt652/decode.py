"""Independent little-endian reader. Format validity does not prove a flush."""
import struct
import zlib

MAGIC = b'XWN652R1'
GROUPS = (('request', 72, 8), ('state', 104, 9), ('trace', 140, 63),
          ('pre', 392, 47), ('post', 580, 47))


def decode(blob, attempt, candidate_sha256):
    def require(ok, message):
        if not ok:
            raise ValueError(message)

    require(len(blob) == 1536, 'exact slot length required')
    require(len(attempt) == 16 and any(attempt), 'attempt identity required')
    require(len(candidate_sha256) == 32 and any(candidate_sha256), 'candidate identity required')
    payload, commit = blob[:1024], blob[1024:]
    require(payload[:8] == MAGIC and commit[:8] == b'XWN652C1', 'magic')
    require(struct.unpack_from('<II', payload, 8) == (1, 768), 'payload version/used')
    require(struct.unpack_from('<II', commit, 8) == (1, 1024), 'commit version/length')
    for part in (payload, commit):
        require(part[16:32] == attempt and part[32:64] == candidate_sha256, 'identity')
    require(not any(payload[768:]) and not any(commit[68:508]), 'reserved bytes')
    require(struct.unpack_from('<I', commit, 64)[0] == zlib.crc32(payload), 'payload CRC')
    require(struct.unpack_from('<I', commit, 508)[0] == zlib.crc32(commit[:508]), 'commit CRC')
    result, post_kind = struct.unpack_from('<iI', payload, 64)
    require(result in (-1, 0, 1) and post_kind in (1, 2), 'result/phase')
    return dict(format_valid=True, physical_observation_not_established=True,
                flush_acknowledgment_not_established=True,
                attempt=attempt.hex(), candidate_sha256=candidate_sha256.hex(),
                result=result, post_kind=post_kind,
                **{name: list(struct.unpack_from('<' + 'I' * count, payload, offset))
                   for name, offset, count in GROUPS})
