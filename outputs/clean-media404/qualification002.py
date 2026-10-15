"""Add actual independent raw-hive agreement; retain typed-decoder failure."""
from qualification import qualify as original

def qualify(first, final, media_kernel, probe_sha256):
    result = original(first, final, media_kernel, probe_sha256)
    agreement = all(h.get('independent_raw_values_agree') is True
                    for r in [first, final] for h in r.get('hives', []))
    typed = all(r.get('typed_decode_complete') is True for r in [first, final])
    result['gates']['independent_raw_hive_agreement'] = agreement
    result['clean_pc_install_scoped_passed'] &= agreement
    result['typed_decode_complete'] = typed
    result['strict_clean_pc_passed'] &= agreement and typed
    result['automatic_runonce_handoff_passed'] = False
    result['disk_only_witness_invocation'] = 'Manual ordinary Windows Run dialog; original scheduled entry absent after setup'
    result['scope'] += '; complete typed value decoding remains a separate strict gate'
    return result
