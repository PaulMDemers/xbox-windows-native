"""Separate clean-PC installation scope from strict events and Xbox assembly."""
def qualify(first, final, media_kernel, probe_sha256):
    def marker(audit, name, phase, cd):
        m = audit.get('markers', {}).get(name, {})
        expected = dict(phase=phase, version='5.0.2195', setup_in_progress='0',
                        setup_type='0', copy='1', runonce='1', cd_readable=str(cd),
                        shutdown_privilege='1', shutdown_api_accepted='1')
        return all(m.get(k) == v for k, v in expected.items())
    def structure(audit):
        hives = audit.get('hives', [])
        return (audit.get('unchanged_by_audit') is True and
                audit.get('setup', {}).get('SystemSetupInProgress') == 0 and
                audit.get('setup', {}).get('SetupType') == 0 and
                len(hives) == 5 and {h['name'] for h in hives} == {'system', 'software', 'sam', 'security', 'default'} and
                all(h['header_valid'] and h['clean'] and h['parsed_keys'] > 0 for h in hives) and
                audit.get('versions', {}).get('ntoskrnl.exe') == media_kernel and
                audit.get('files', {}).get('xwn404.exe', {}).get('sha256') == probe_sha256 and
                audit.get('qcow_check', {}).get('check-errors') == 0 and
                not any(audit.get('qcow_check', {}).get(k, 0) for k in ['corruptions', 'leaks', 'check-errors']))
    history = True
    for group in ['system', 'application']:
        current = {r['record']: r for r in final.get('events', {}).get(group, [])}
        history &= all(current.get(r['record']) == r for r in first.get('events', {}).get(group, []))
    gates = dict(first_logon=marker(first, 'xwn404-setup.txt', 'setup-logon', 1),
                 disk_only_logon=marker(final, 'xwn404-boot.txt', 'disk-only-logon', 0),
                 first_marker_preserved=first.get('markers', {}).get('xwn404-setup.txt') == final.get('markers', {}).get('xwn404-setup.txt'),
                 first_structure=structure(first), final_structure=structure(final),
                 event_history_preserved=history,
                 first_normal_shutdown=first.get('normal_shutdown_events', 0) >= 1,
                 second_normal_shutdown=final.get('normal_shutdown_events', 0) == first.get('normal_shutdown_events', 0) + 1)
    scoped = all(gates.values())
    return dict(gates=gates, clean_pc_install_scoped_passed=scoped,
                strict_events_passed=not final.get('warnings_errors', []),
                strict_clean_pc_passed=scoped and not final.get('warnings_errors', []),
                fresh_xbox_assembly_qualified=False, physical_qualified=False,
                scope='Ordinary PC setup/logon and media-detached boot with selected cold checks; no complete NTFS allocation or Xbox assembly qualification')
