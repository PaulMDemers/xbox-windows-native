# Cursor position within the same client

Fresh matched ordinary children, same explicit visible standard arrow. Inside is
512,288; outside is820,460, outside the largest copied screen rectangle ending
at807,442 but inside the same client. No cursor hiding or driver/settings changes.
Both run the same54 cases/162 full RGB checks and verify cursor flags, exact
position and handle in each loop. Query/state failures log actual flags/position
and handles; uncover and initialization failures have separate labels.

This follows CLOSED outside001 in video-cursor-profile: FAIL_INITIALIZE before
any timing, responsive desktop, manually restarted. Its compound check did not
identify which initialization predicate failed; desktop cursor ownership is only
a hypothesis. That failed case is never relaunched and remains unqualified.

Use fresh output109, CREATE_NEW, frozen source/binary/fixture pins, full cold
allocation/hive/protected/event/config/pagefile checks. No host UI/debugger during
ordinary measurement. One run per position/three rotated rounds does not provide
hardware speed or an isolated bandwidth estimate. No speculative driver change.
