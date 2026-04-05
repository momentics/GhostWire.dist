param(
    [Parameter(Mandatory = $true)]
    [string]$Version,

    [Parameter(Mandatory = $true)]
    [string]$Asset
)

$baseUrl = "https://github.com/momentics/GhostWire.dist/releases/download/$Version"
$url = "$baseUrl/$Asset"

Write-Host "Fetching $Asset from $baseUrl"
Invoke-WebRequest -Uri $url -OutFile $Asset
