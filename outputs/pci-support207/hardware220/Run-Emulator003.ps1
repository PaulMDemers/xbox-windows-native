#requires -Version 7.4
$ErrorActionPreference='Stop'
if((Get-PSDrive C).Free - 128MB -lt 20GB){throw '20GiB projected guard'}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource xemu -Action {
 & C:/Python314/python.exe (Join-Path $PSScriptRoot 'run-emulator003.py')
 if($LASTEXITCODE){throw 'Inventory rehearsal failed; cold audit required'}
}
