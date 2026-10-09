"""Explicit experimental interval permission; warnings never pass strict qualification."""
FIELDS = ['source', 'event_id', 'type', 'strings', 'data_hex']


def signature(event):
    return {name: event[name] for name in FIELDS}


def documented_only(warnings, documented):
    actual = [signature(v) for v in warnings]
    return (all(v in documented for v in actual)
            and all(actual.count(v) <= 1 for v in documented))


def measurement_events(log, events):
    def unix_time(label):
        rows = [v.split() for v in log.splitlines() if v.startswith(label + ' ')]
        assert len(rows) == 1
        _, low, high = rows[0]
        low, high = int(low), int(high)
        assert 0 <= low <= 0xffffffff and 0 <= high <= 0xffffffff
        return ((high << 32) | low) // 10000000 - 11644473600
    start, end = unix_time('MEASUREMENT_START_TIME'), unix_time('MEASUREMENT_END_TIME')
    assert 0 <= start <= end
    inside = [v for v in events if v['type'] in [1, 2]
              and start - 1 <= v['generated_unix'] <= end + 1]
    return [start, end], inside


def candidate_permitted(audit, hives, restored):
    return (audit.get('scoped_display_passed') is True
            and audit.get('warnings_are_documented_baseline_only') is True
            and hives.get('passed') is True and restored.get('passed') is True)
