#requires -Version 7.4
param([Parameter(Mandatory)][ValidatePattern('^[a-z0-9]+$')][string]$Case,
      [ValidateSet('conexant','xcalibur')][string]$Encoder='conexant')
$ErrorActionPreference='Stop'
if((Get-PSDrive C).Free - 128MB -lt 20GB){throw '20GiB projected guard'}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource xemu -Action {
    & C:/Python314/python.exe (Join-Path $PSScriptRoot 'model-test.py') --case $Case --encoder $Encoder
    if($LASTEXITCODE){throw 'Model test failed; preserve case'}
}
