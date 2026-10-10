param([Parameter(Mandatory)][ValidatePattern('^emu[0-9]{3}$')][string]$Case)
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$run="$repo/work/runs/nt5xidrestart-$Case"
if(Test-Path $run){throw 'Never reuse preparation ID'}
if((Get-Content "$repo/.git/HEAD" -Raw).Trim() -ne 'ref: refs/heads/codex/xbox-native-usb'){throw 'Wrong branch'}
if((Get-PSDrive C).Free -lt (20GB+64MB)){throw '20 GiB projected guard'}
$seed="$repo/outputs/usb-identification207/artifacts/emu001/seed.qcow2"
if((Get-FileHash $seed).Hash.ToLowerInvariant() -ne '7c09d05af676a7c37f242850837a8b2fa19b81a6ae63b2af2ec156e9a5fa197b'){throw 'Seed drift'}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 New-Item -ItemType Directory $run | Out-Null
 $linuxRun=('/mnt/e'+$run.Substring(2)).Replace('\','/')
 $linuxScript=('/mnt/e'+$PSScriptRoot.Substring(2)).Replace('\','/')+'/emulator-disk.py'
 & wsl -d Ubuntu --cd $linuxRun -- qemu-img create -f qcow2 -F qcow2 -b ../../../outputs/usb-identification207/artifacts/emu001/seed.qcow2 hdd.qcow2
 if($LASTEXITCODE){throw 'Overlay create failed'}
 & wsl -d Ubuntu -- env PYTHONDONTWRITEBYTECODE=1 python3 $linuxScript stage $Case
 if($LASTEXITCODE){throw 'Staging/audit failed; no launch'}
}
