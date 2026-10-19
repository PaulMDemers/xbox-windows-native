"""MIT. Offline review of completed physical RCT565 evidence; no console access."""
import datetime
import hashlib
import json
from pathlib import Path

K = Path(__file__).resolve().parent


def read(name):
    return json.loads((K / name).read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = K / "closeout-review001.json"
    assert not out.exists()
    stage = read("stage004.json")
    collection = read("collection002.json")
    audit = read("audit1.json")
    registry = read("registry-review001.json")
    supervisor = read("supervisor-tail001.json")
    assert stage["completed"] and collection["completed"]
    assert supervisor["completed"] and supervisor["closed"]
    assert collection["hook_removed"] and collection["protected_code_exact"]
    assert audit["closed"] and audit["hives_clean"]
    assert registry["passed"] and registry["game_registry_subtree_restored"]
    assert audit["after_sha256"] == sha(K / "collection002.json")
    runner = collection["files"]["/E/xwn565/runner.txt"]
    path = Path(runner["path"])
    assert sha(path) == runner["sha256"]
    lines = path.read_text(encoding="ascii").splitlines()
    numbers = {}
    windows = []
    for line in lines:
        if line.startswith("window "):
            windows.append(line)
        else:
            key, value = line.split("=", 1)
            numbers.setdefault(key, []).append(int(value))
    graceful_exit = numbers.get("game_exit") == [0] and "forced_terminate" not in numbers
    requested_restart = numbers.get("restart_requested") == [1]
    restored = numbers.get("registry_restored") == [1]
    observation = read("observation001.json")
    dashboard = observation["completed"] and observation["result"] == "dashboard_with_runner_receipt"
    changed = {
        name: {"before_sha256": prior["sha256"],
               "after_sha256": collection["files"][name]["sha256"]}
        for name, prior in stage["staged"].items()
        if prior["sha256"] != collection["files"][name]["sha256"]
    }
    added_game_files = sorted(set(collection["game_rows"]) - set(stage["staged"]))
    immutable_changes = [name for name in changed
                         if name not in ("/E/xwn565-kit/game/Data/Game.cfg",
                                         "/E/xwn565-kit/game/Data/CSS0.DAT")]
    events = {name: [dict(record=r["record"], source=r["source"], event_id=r["event_id"])
                    for r in details["new_records"]]
              for name, details in audit["events"].items()}
    normal_shutdown_delta = audit["events"]["system"]["normal_shutdown_delta"]
    evidence_names = ["stage004.json", "launch001.json", "observation001.json",
                      "user-observation001.json", "collection002.json", "audit1.json",
                      "registry-review001.json", "supervisor-tail001.json"]
    result = dict(
        completed=True, utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        source_sha256=sha(Path(__file__)),
        evidence_sha256={name: sha(K / name) for name in evidence_names},
        runner_sha256=runner["sha256"], runner_numeric_records=numbers,
        runner_window_records=sorted(set(windows)),
        game_graceful_exit=graceful_exit, registry_restored=restored,
        dashboard_return=dashboard, normal_shutdown_delta=normal_shutdown_delta,
        normal_restart_supported=(requested_restart and dashboard and normal_shutdown_delta == 1),
        changed_staged_files=changed, added_game_files=added_game_files,
        immutable_payload_changes=immutable_changes, events=events,
        event_scope=audit["events"]["system"]["scope"],
        console_access=False, whole_allocation_audit=False,
        rendering_evidence="Separate user observation; exit code and window title alone do not prove rendering",
        graphics_api_trace=False, gpu_acceleration_qualified=False)
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
