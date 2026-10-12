$ErrorActionPreference='Stop'
$checks=0
$guard={param($ManualCapture,$CaptureWidth,$CaptureHeight,$CapturePitch)
# Automatic legacy capture stays limited to four MiB. This ordinary run uses
# explicit ManualCapture geometry and guest logs, not host framebuffer reads.
$manualHdGeometry = $ManualCapture -and $CaptureWidth -eq 1920 -and $CaptureHeight -eq 1080 -and $CapturePitch -eq 7680
if ($CapturePitch -lt $CaptureWidth * 4 -or $CapturePitch % 4 -ne 0 -or
    ($CapturePitch * $CaptureHeight -gt 4MB -and -not $manualHdGeometry) -or
    $CapturePitch * $CaptureHeight -gt (9MB - 316160)) {
    throw 'Capture geometry exceeds the legacy capture or explicit manual HD layout.'
}
}
foreach($row in @(@($true,1920,1080,7680,$true),@($false,1920,1080,7680,$false),@($true,1920,1080,7684,$false),@($true,1920,1081,7680,$false),@($true,1280,720,5120,$true),@($false,1280,720,5120,$true),@($true,1920,1080,7676,$false),@($true,1920,1080,7681,$false))){
 $ok=$true;try{& $guard $row[0] $row[1] $row[2] $row[3]}catch{$ok=$false}
 if($ok -ne $row[4]){throw 'Geometry preflight mismatch'};$checks++
}
@{passed=$true;actual_guard_cases=$checks;scope='Exact host guard, modeled scalar parameters; no guest reads'} | ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $PSScriptRoot geometry-tests001.json)
Write-Output "Host geometry guard: $checks cases passed"
