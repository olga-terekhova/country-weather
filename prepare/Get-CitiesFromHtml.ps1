[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$SourcePath,
    [Parameter(Mandatory)][string]$OutputPath,
    [Parameter(Mandatory)][string]$UrlAppend
)

# Preprocess 1: resolve source path and verify it exists
if (-not [System.IO.Path]::IsPathRooted($SourcePath)) {
    $SourcePath = Join-Path (Get-Location) $SourcePath
}
Write-Host "Source file: $SourcePath"
if (-not (Test-Path $SourcePath)) {
    Write-Error "Source file not found: $SourcePath"
    exit 1
}

# Preprocess 2: resolve output path and create directories if needed
if (-not [System.IO.Path]::IsPathRooted($OutputPath)) {
    $OutputPath = Join-Path (Get-Location) $OutputPath
}
$outputDir = Split-Path $OutputPath -Parent
if ($outputDir -and -not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    Write-Host "Created directory: $outputDir"
}

# Preprocess 3: remove trailing slash from url-append
$UrlAppend = $UrlAppend.TrimEnd('/')

# Process
$content = Get-Content -Path $SourcePath -Raw -Encoding UTF8

$matches_ = [regex]::Matches($content, '<a href="(/prognoz/([^/]+)/)">')

$rows = foreach ($m in $matches_) {
    $href     = $m.Groups[1].Value
    $cityName = $m.Groups[2].Value
    $cityUrl  = $UrlAppend + $href
    [PSCustomObject]@{
        'city-name' = $cityName
        'city-url'  = $cityUrl
    }
}

# Save to CSV
if (Test-Path $OutputPath) {
    Write-Warning "Output file already exists and will be overwritten: $OutputPath"
}

$rows | Export-Csv -Path $OutputPath -NoTypeInformation -Encoding UTF8 -Force

Write-Host "Saved $($rows.Count) cities to $OutputPath"
