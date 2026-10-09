#requires -Version 7.4
$ErrorActionPreference='Stop'
$p='/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/setup-wizard-automation201'
if(Test-Path (Join-Path $PSScriptRoot policy-tests.json)){throw 'Already tested'}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & wsl -d Ubuntu -- gcc -std=c11 -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined -o ($p+'/artifacts/policy-tests') ($p+'/test-policy.c')
 if($LASTEXITCODE){throw 'Host compilation failed'}
 $result=& wsl -d Ubuntu -- ($p+'/artifacts/policy-tests')
 if($LASTEXITCODE){throw 'Policy tests failed; preserve'}
 $result | Set-Content (Join-Path $PSScriptRoot policy-tests-console.txt)
 @{passed=$true;scope='Host actual-header ASan/UBSan exact command/window adversaries only, no guest or UI';output=$result;source_sha256=(Get-FileHash (Join-Path $PSScriptRoot policy.h)).Hash.ToLowerInvariant();test_sha256=(Get-FileHash (Join-Path $PSScriptRoot test-policy.c)).Hash.ToLowerInvariant();physical_access=$false} | ConvertTo-Json | Set-Content (Join-Path $PSScriptRoot policy-tests.json)
}
