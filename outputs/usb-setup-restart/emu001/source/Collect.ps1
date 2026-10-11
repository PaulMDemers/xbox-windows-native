param([ValidateSet('emu001','emu002')][string]$Case)
$ErrorActionPreference='Stop'
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 $base=('/mnt/e'+$PSScriptRoot.Substring(2)).Replace('\','/')
 wsl -d Ubuntu -- python3 -B "$base/disk.py" audit $Case
 if($LASTEXITCODE){throw 'Cold disk audit failed'}
 foreach($script in @('audit-details.py','typed-state.py','no-xid-state.py','forensics.py','cold-sectors.py','cold-ranges.py')) {
  wsl -d Ubuntu -- env LD_LIBRARY_PATH=/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu python3 -B "$base/$script" $Case
  if($LASTEXITCODE){throw "Cold collection failed: $script"}
 }
}
foreach($script in @('setup-evidence.py','qualify.py','analyze-trace.py','parse-transfer.py','compare-transfer.py','compare-phases.py','qcow-evidence.py')) {
 C:/Python314/python.exe -B "$PSScriptRoot/$script" $Case > "$PSScriptRoot/artifacts/$Case-$script.console.txt"
 if($LASTEXITCODE){throw "Closed trace analysis failed: $script"}
}
