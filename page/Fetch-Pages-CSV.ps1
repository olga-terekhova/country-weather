[CmdletBinding()]
param (
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$SourceFilePath,

    [Parameter(Mandatory = $true, Position = 1)]
    [string]$UrlColumn,

    [Parameter(Mandatory = $true, Position = 2)]
    [string]$FileNameColumn,

    [Parameter(Mandatory = $false)]
    [int]$WaitSeconds = 10,

    [Parameter(Mandatory = $false)]
    [string]$Range = ":"
)

# Preprocess 1: resolve and validate source file path
$localDirectory = (Get-Location).Path

if ([System.IO.Path]::IsPathRooted($SourceFilePath)) {
    $absoluteSourcePath = $SourceFilePath
} else {
    $absoluteSourcePath = Join-Path -Path $localDirectory -ChildPath $SourceFilePath
}

Write-Host "Source file: $absoluteSourcePath"

if (-not (Test-Path -Path $absoluteSourcePath)) {
    Write-Error "Source file not found: '$absoluteSourcePath'"
    exit 1
}

# Preprocess 2: derive output directory name and create it
$baseName = [System.IO.Path]::GetFileNameWithoutExtension($SourceFilePath)
$outputDirectory = Join-Path -Path $localDirectory -ChildPath $baseName

if (Test-Path -Path $outputDirectory) {
    Write-Warning "Output directory already exists: '$outputDirectory'"
} else {
    New-Item -ItemType Directory -Path $outputDirectory | Out-Null
}

# Preprocess 3: parse range parameter
$rangeParts = $Range -split ':'
if ($rangeParts.Count -ne 2) {
    Write-Error "Invalid range '$Range'. Expected format: 'start:stop' (e.g. '1:10', ':2', ':')."
    exit 1
}

$rangeStartStr = $rangeParts[0].Trim()
$rangeStopStr  = $rangeParts[1].Trim()

$rangeStart = 0
if ($rangeStartStr -ne '') {
    if (-not [int]::TryParse($rangeStartStr, [ref]$rangeStart)) {
        Write-Error "Invalid range start '$rangeStartStr'. Must be a non-negative integer."
        exit 1
    }
}

$rangeStopIsOpen = ($rangeStopStr -eq '')
$rangeStop = 0
if (-not $rangeStopIsOpen) {
    if (-not [int]::TryParse($rangeStopStr, [ref]$rangeStop)) {
        Write-Error "Invalid range stop '$rangeStopStr'. Must be a non-negative integer."
        exit 1
    }
}

# Process 1: read CSV, validate columns and range
$allRows = @(Import-Csv -Path $absoluteSourcePath)

if ($allRows.Count -eq 0) {
    Write-Error "The file '$absoluteSourcePath' is empty or contains only a header row."
    exit 1
}

$columnNames = $allRows[0].PSObject.Properties.Name
if ($columnNames -notcontains $UrlColumn) {
    Write-Error "Column '$UrlColumn' not found in '$absoluteSourcePath'."
    exit 1
}
if ($columnNames -notcontains $FileNameColumn) {
    Write-Error "Column '$FileNameColumn' not found in '$absoluteSourcePath'."
    exit 1
}

$totalRows = $allRows.Count

if ($rangeStopIsOpen) {
    $rangeStop = $totalRows
}

if ($rangeStart -lt 0 -or $rangeStop -gt $totalRows -or $rangeStart -ge $rangeStop) {
    Write-Error "Range '$Range' is out of bounds. File has $totalRows data row(s) (indices 0 to $($totalRows - 1))."
    exit 1
}

$selectedRows = $allRows[$rangeStart..($rangeStop - 1)]

# Process 2: download pages
$isFirst = $true
foreach ($row in $selectedRows) {
    $url = $row.$UrlColumn
    $outputFileName = $row.$FileNameColumn
    $outputFilePath = Join-Path -Path $outputDirectory -ChildPath $outputFileName

    if (-not $isFirst) {
        Write-Host "Waiting $WaitSeconds seconds before the next download"
        Start-Sleep -Seconds $WaitSeconds
    }
    $isFirst = $false

    if (Test-Path -Path $outputFilePath) {
        Write-Warning "Output file '$outputFilePath' already exists, overwriting."
    }

    try {
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing
        Set-Content -Path $outputFilePath -Value $response.Content -Encoding UTF8
        Write-Host "$url saved to $outputFilePath"
    }
    catch {
        Write-Error "Failed to download '$url'. Error: $_"
    }
}
