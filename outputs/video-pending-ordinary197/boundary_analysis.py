"""Fail-closed actual194 lifecycle and byte-exact checkpoint analysis."""
GUIDANCE = [
    'Close known hardware wizards without disabling devices. Leave this window visible.',
    'Waiting up to fifteen minutes for five seconds of actual setup idle.']
LIMIT = 16 * 1024 * 1024


def analyze(log, snapshots):
    result = dict(idle_branch_passed=False, pending_branch_passed=False,
                  checkpoint_equal=False, preflight_status_transitions=[])
    try:
        lines = (log or '').splitlines()
        at = 0

        def exact(line):
            nonlocal at
            assert at < len(lines) and lines[at] == line
            at += 1

        def number(label):
            nonlocal at
            values = lines[at].split()
            assert len(values) == 2 and values[0] == label
            value = int(values[1])
            assert 0 <= value <= 0xffffffff
            at += 1
            return value

        def timestamp(label):
            nonlocal at
            values = lines[at].split()
            assert len(values) == 3 and values[0] == label
            low, high = (int(v) for v in values[1:])
            assert 0 <= low <= 0xffffffff and 0 <= high <= 0xffffffff
            at += 1
            return (high << 32) | low

        exact('ATTEMPT_ONCE')
        exact('WAITING_FOR_SETUP_IDLE')
        for line in GUIDANCE:
            exact(line)
        wait_start = timestamp('SETUP_WAIT_START_TIME')
        transitions = result['preflight_status_transitions']
        while at < len(lines) and lines[at].startswith('INSTALL_PREFLIGHT_RESULT '):
            value = number('INSTALL_PREFLIGHT_RESULT')
            assert value in (0, 258)
            transitions.append(value)
        assert transitions
        if at < len(lines) and lines[at].startswith('MEASUREMENT_BLOCKED_SETUP_TIMEOUT '):
            elapsed = number('MEASUREMENT_BLOCKED_SETUP_TIMEOUT')
            result['pending_branch_passed'] = (elapsed >= 900000 and 258 in transitions
                and at == len(lines) and snapshots == [None, None])
            result['timeout_ms'] = elapsed
            return result
        idle = number('SETUP_IDLE_OBSERVED_MS')
        elapsed = number('SETUP_WAIT_ELAPSED_MS')
        assert transitions[-1] == 0 and 5000 <= idle <= elapsed < 900000

        def checkpoint():
            assert number('INSTALL_BEFORE_CHECKPOINT') == 0
            assert number('INSTALL_AFTER_CHECKPOINT') == 0
            return timestamp('CHECKPOINT_TIME'), number('CHECKPOINT_SOURCE_BYTES')

        before_time, before_size = checkpoint()
        start_time = timestamp('MEASUREMENT_START_TIME')
        exact('MEASUREMENT_BEGIN')
        for i in range(5):
            exact('INSTALL_BEFORE_SAMPLE 0')
            exact('SAMPLE_EXIT_ZERO %d' % i)
            exact('INSTALL_AFTER_SAMPLE 0')
        after_time, after_size = checkpoint()
        end_time = timestamp('MEASUREMENT_END_TIME')
        exact('INSTALL_WAIT_RESULT 0')
        exact('INSTALL_FINAL_RESULT 0')
        exact('NORMAL_RESTART_REQUEST 0')
        assert at == len(lines)
        assert 0 < wait_start <= before_time <= start_time <= after_time <= end_time
        assert len(snapshots) == 2 and all(isinstance(v, bytes) for v in snapshots)
        assert 0 <= before_size == after_size <= LIMIT
        assert len(snapshots[0]) == before_size and len(snapshots[1]) == after_size
        result['checkpoint_equal'] = snapshots[0] == snapshots[1]
        result.update(setup_idle_ms=idle, setup_wait_ms=elapsed,
                      checkpoint_size=before_size, idle_branch_passed=result['checkpoint_equal'])
    except (AssertionError, IndexError, ValueError, TypeError) as exc:
        result['refusal'] = type(exc).__name__
    return result
