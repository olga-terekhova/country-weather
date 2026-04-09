[CmdletBinding()]
param (
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$FileName,

    [Parameter(Mandatory = $false, Position = 1)]
    [int]$WaitSeconds = 10
)

$localDirectory = (Get-Location).Path
$inputFilePath = Join-Path -Path $localDirectory -ChildPath $FileName

$baseName = [System.IO.Path]::GetFileNameWithoutExtension($FileName)
$outputDirectory = Join-Path -Path $localDirectory -ChildPath $baseName

if (Test-Path -Path $outputDirectory) {
    Write-Error "Output directory already exists: '$outputDirectory'. Remove it or choose a different input file."
    exit 1
}

New-Item -ItemType Directory -Path $outputDirectory | Out-Null

$lines = @(Get-Content -Path $inputFilePath)
$lastDownloadIndex = -1

for ($i = 0; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]
    $tokens = $line -split '\s+' | Where-Object { $_ -ne '' }

    if ($tokens.Count -eq 0) {
        Write-Warning "Line $($i + 1): empty line, skipping."
        continue
    }

    if ($tokens.Count -eq 1) {
        Write-Warning "Line $($i + 1): only one token found ('$($tokens[0])'), skipping."
        continue
    }

    if ($tokens.Count -gt 2) {
        Write-Warning "Line $($i + 1): more than two tokens found, skipping."
        continue
    }

    $url = $tokens[0]
    $outputFileName = $tokens[1]
    $outputFilePath = Join-Path -Path $outputDirectory -ChildPath $outputFileName

    if (Test-Path -Path $outputFilePath) {
        Write-Warning "Line $($i + 1): output file '$outputFilePath' already exists, overwriting."
    }

    if ($lastDownloadIndex -ge 0) {
        Write-Host "Waiting $WaitSeconds seconds before the next download"
        Start-Sleep -Seconds $WaitSeconds
    }

    try {
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing
        Set-Content -Path $outputFilePath -Value $response.Content -Encoding UTF8
        Write-Host "$url saved to $outputFilePath"
        $lastDownloadIndex = $i
    }
    catch {
        Write-Error "Line $($i + 1): failed to download '$url'. Error: $_"
    }
}
