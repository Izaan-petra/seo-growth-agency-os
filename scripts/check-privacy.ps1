[CmdletBinding()]
param(
    [ValidateSet('Staged', 'Tracked', 'Workspace')]
    [string]$Mode = 'Staged'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repositoryRoot = Split-Path -Parent $PSScriptRoot
$allowlistPath = Join-Path $repositoryRoot '.privacy-allowlist'
$allowlist = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)

if (Test-Path -LiteralPath $allowlistPath -PathType Leaf) {
    foreach ($line in Get-Content -LiteralPath $allowlistPath -Encoding UTF8) {
        $candidate = $line.Trim().Replace('\', '/')
        if ($candidate -and -not $candidate.StartsWith('#')) {
            [void]$allowlist.Add($candidate)
        }
    }
}

if ($Mode -eq 'Staged') {
    $relativePaths = @(git -C $repositoryRoot diff --cached --name-only --diff-filter=ACMR)
} elseif ($Mode -eq 'Tracked') {
    $relativePaths = @(git -C $repositoryRoot ls-files)
} else {
    $relativePaths = @(
        git -C $repositoryRoot ls-files
        git -C $repositoryRoot ls-files --others --exclude-standard
    ) | Sort-Object -Unique
}

if ($LASTEXITCODE -ne 0) {
    throw "Unable to enumerate $Mode repository files."
}

$errors = [System.Collections.Generic.List[string]]::new()
$artifactPattern = '^(?:reports/|research/(?:raw|processed|snapshots|cache)/|clients/|logs/)'
$allowedSentinelPattern = '/?\.gitkeep$'
$binaryExtensions = @('.zip', '.png', '.jpg', '.jpeg', '.gif', '.pdf', '.xlsx', '.xls', '.parquet', '.db', '.sqlite')
$opaqueDataExtensions = @('.zip', '.xlsx', '.xls', '.parquet', '.db', '.sqlite')
$secretPatterns = @(
    @{ Id = 'private-key'; Pattern = '-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----' }
    @{ Id = 'bearer-token'; Pattern = '(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{20,}' }
    @{ Id = 'github-token'; Pattern = '\b(?:ghp|gho|ghu|ghs|github_pat)_[A-Za-z0-9_]{20,}\b' }
    @{ Id = 'aws-access-key'; Pattern = '\b(?:AKIA|ASIA)[A-Z0-9]{16}\b' }
    @{ Id = 'credential-assignment'; Pattern = '(?i)(?:api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|password)["'']?\s*[:=]\s*["'']?[A-Za-z0-9/+_.=-]{12,}' }
)

foreach ($rawPath in $relativePaths) {
    $relativePath = ([string]$rawPath).Trim().Replace('\', '/')
    if (-not $relativePath) {
        continue
    }

    $isAllowlisted = $allowlist.Contains($relativePath)
    if ($relativePath -match $artifactPattern -and $relativePath -notmatch $allowedSentinelPattern -and -not $isAllowlisted) {
        $errors.Add("Client/generated artifact is not allowed in Git: $relativePath")
        continue
    }

    if ($isAllowlisted) {
        continue
    }

    $fullPath = Join-Path $repositoryRoot $relativePath
    if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
        continue
    }
    $extension = [System.IO.Path]::GetExtension($fullPath).ToLowerInvariant()
    if ($extension -in $opaqueDataExtensions) {
        $errors.Add("Opaque data file requires an explicit privacy allowlist decision: $relativePath")
        continue
    }
    if ($extension -in $binaryExtensions) {
        continue
    }

    $lineNumber = 0
    foreach ($line in Get-Content -LiteralPath $fullPath -Encoding UTF8) {
        $lineNumber++
        if ($line -match 'synthetic-secret-fixture') {
            continue
        }
        foreach ($rule in $secretPatterns) {
            if ($line -match $rule.Pattern) {
                $errors.Add("Potential $($rule.Id) in ${relativePath}:$lineNumber")
            }
        }
    }
}

if ($errors.Count -gt 0) {
    $errors | ForEach-Object { Write-Error $_ }
    exit 1
}

Write-Output "Privacy and secret check passed for $($relativePaths.Count) $($Mode.ToLowerInvariant()) files."
