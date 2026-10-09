#requires -Version 7.4
$ErrorActionPreference='Stop'
if((Get-PSDrive C).Free -lt 20GB){throw '20GiB guard'}
$kit=$PSScriptRoot.Replace('\','/').Replace('C:','/mnt/c')
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
    foreach($call in @(@('prepare-parent.py'),@('prepare.py','control001'),@('prepare.py','candidate001'))){
        $file=$kit+'/'+$call[0]
        $arguments=@($call | Select-Object -Skip 1)
        & wsl -d Ubuntu -- env LD_LIBRARY_PATH=/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu python3 $file @arguments
        if($LASTEXITCODE -ne 0){throw ('Preparation failed; preserve actual state: '+$call[0])}
    }
}
