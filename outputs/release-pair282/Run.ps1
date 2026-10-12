#requires -Version 7.4
param([ValidateSet('control001','candidate001')][string]$Case)
$ErrorActionPreference='Stop'
$env:PYTHONUTF8='1'
$out=Join-Path $PSScriptRoot $Case
$f=Get-Content (Join-Path $out prepared.json) -Raw | ConvertFrom-Json
$root=$f.root
if(Test-Path (Join-Path $out runner-start.json)){throw 'Consumed282 launch'}
if((Get-PSDrive C).Free-64MB -lt 20GB){throw '20GiB C guard'}
if((Get-PSDrive E).Free-512MB -lt 20GB){throw '20GiB E guard'}
foreach($p in $f.dependencies.PSObject.Properties){if((Get-FileHash $p.Name).Hash.ToLowerInvariant() -ne $p.Value){throw ('Dependency changed: '+$p.Name)}}
foreach($p in $f.inputs.PSObject.Properties){if((Get-FileHash (Join-Path $root $p.Name)).Hash.ToLowerInvariant() -ne $p.Value.sha256){throw ('Input changed: '+$p.Name)}}
if($env:XWN_REUSE269_DIR -or $env:XWN_NATIVE_EVENT_LOG -or $env:XWN_NV2A_RESOURCE_MODEL){throw 'Unexpected diagnostic environment'}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource xemu -Shared -Action {
    $process=$null;$controller=$null;$fallback=$false
    $env:XWN_REUSE269_DIR=(Join-Path $root watch)
    try {
        @{utc=[DateTime]::UtcNow.ToString('o');owner_pid=$PID;physical_access=$false} | ConvertTo-Json | Set-Content (Join-Path $out runner-start.json)
        $process=& C:/Users/Paul/Desktop/ogxbox-linux/scripts/start_xemu_instance.ps1 -TaskId release-pair282 -XemuPath (Join-Path $root xemu.exe) -ConfigPath (Join-Path $root config.toml) -RunDirectory $root -InstanceRoot E:/xwn282/instances -ScratchRoot E:/xwn282/scratch -ArgumentList @('-dvd_path',(Join-Path $root control.iso),'-S','-gdb','tcp:127.0.0.1:4825','-monitor','tcp:127.0.0.1:4824,server,nowait','-net','none')
        $controller=Start-Process C:/Python314/python.exe -ArgumentList @('-B',('"'+(Join-Path $PSScriptRoot trace.py)+'"'),$Case) -PassThru -WindowStyle Hidden -RedirectStandardOutput (Join-Path $out controller.stdout.log) -RedirectStandardError (Join-Path $out controller.stderr.log)
        if(-not $controller.WaitForExit(480000)){ $controller.Kill();$controller.WaitForExit();throw 'Owned controller480second watchdog' }
        if(-not $process.WaitForExit(15000)){throw 'Host failed orderly quit'}
    } finally {
        if($controller -and -not $controller.HasExited){$controller.Kill();$controller.WaitForExit()}
        if($process -and -not $process.HasExited){$fallback=$true;$process.Kill();$process.WaitForExit()}
        Remove-Item Env:XWN_REUSE269_DIR -ErrorAction SilentlyContinue
        @{utc=[DateTime]::UtcNow.ToString('o');closed=$true;fallback_kill=$fallback;host_exit=$(if($process){$process.ExitCode}else{$null});controller_exit=$(if($controller){$controller.ExitCode}else{$null})} | ConvertTo-Json | Set-Content (Join-Path $out host-closure.json)
    }
}
