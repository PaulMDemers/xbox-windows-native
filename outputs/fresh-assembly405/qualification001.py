"""Independent final gates; functional success never erases strict failures."""
def qualify(audit,launch,network,assembly,base):
    w=audit.get('witness',{});alloc=audit.get('allocation',{})
    exact={'BEGIN':405,'COMPLETE':405,'PERSISTENCE':1,'WIDTH':1280,'HEIGHT':720,'BPP':32,
           'MEMORY_GDI':1,'NETWORK_RESULT':0,'WAVE_DEVICES':1,'AUDIO_RESULT':0,
           'SHUTDOWN_PRIVILEGE':1,'NORMAL_RESTART_REQUEST':1}
    cycles=launch.get('cycles',[]);hives=audit.get('hives',[]);protected=audit.get('protected',[])
    events=[r for v in audit.get('events',{}).values() for r in v.get('new',[])]
    failures=[r for r in events if r['type'] in (1,2)]
    host=audit.get('host_exit',{})
    gates=dict(
      witness=all(w.get(k)==v for k,v in exact.items()),
      exact_persistent_bytes=audit.get('checks',{}).get('cold_exact_data') is True,
      network=network.get('passed') is True and network.get('accepted_witnesses')==1 and network.get('rounds')==32 and network.get('bytes_each_direction')==131072,
      single_launch=len(cycles)==1 and cycles[0].get('status')=='accepted' and cycles[0].get('dashboard_return') is True,
      orderly_host=host.get('closed') is True and host.get('exit_code')==0 and host.get('orderly_requested') is True and host.get('fallback_kill') is False and host.get('timeout') is False,
      normal_shutdown=sum(r['source']=='EventLog' and r['event_id']==6006 for r in events)==1,
      event_history=audit.get('checks',{}).get('event_history_preserved') is True,
      allocation=alloc.get('capture_complete') is True and alloc.get('allocation_consistent') is True and alloc.get('orphan_cluster_count')==0 and alloc.get('errors')==[] and alloc.get('capture_chain_warnings')==[],
      five_hives=len(hives)==5 and all(all(h.get(k) is True for k in ['header_valid','clean','independent_raw_values_agree']) for h in hives),
      protected_code=bool(protected) and all(p.get('unchanged') is True and p.get('before')==p.get('after') for p in protected),
      clean_source=base.get('old_windows_payload_used') is False and base.get('source404_sha256')=='ece991e4dc6b662ece2a39dddba384a3c480173cafd89086135f6bb861b7f796',
      normal_startup=assembly.get('diagnostic_startup_absent') is True and assembly.get('all_existing_files_exact_except_removed_startup') is True)
    excluded=[v for v in base.get('explicit_exclusions',[]) if 'FATX component' in v.get('reason','')]
    strict=dict(no_warning_error_events=not failures,lossless_fatx_transfer=not excluded,
                complete_typed_hives=len(hives)==5 and all(h.get('typed_decode_complete') is True for h in hives))
    return dict(gates=gates,fresh_xbox_functional_scoped_pass=all(gates.values()),strict_gates=strict,
                strict_qualification=all(gates.values()) and all(strict.values()),unrepresentable_paths=len(excluded),
                warning_error_events=[dict(source=r['source'],event_id=r['event_id']) for r in failures],
                physical_qualification=False,public_installer_qualified=False)
