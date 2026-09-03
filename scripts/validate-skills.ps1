[CmdletBinding()]
param(
    [string]$PythonPath,
    [switch]$RequirePython
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repositoryRoot = Split-Path -Parent $PSScriptRoot
$skillsRoot = Join-Path $repositoryRoot '.agents\skills'
$errors = [System.Collections.Generic.List[string]]::new()

$skillFiles = Get-ChildItem -LiteralPath $skillsRoot -Filter 'SKILL.md' -File -Recurse
$requiredCoreSkills = @('project-intake', 'seo-director', 'seo-growth-blueprint')
$specialistSkills = @(
    'authority-link-building'
    'competitor-serp-analysis'
    'geo-aeo'
    'keyword-intent-strategy'
    'seo-content-strategy'
    'seo-cro'
    'seo-measurement'
    'technical-seo'
)
$requiredControlFiles = @(
    '.agents\skills\project-intake\integration-catalog.md'
    '.agents\skills\project-intake\authorization-manifest.md'
    '.agents\skills\seo-director\routing-matrix.md'
    '.agents\skills\seo-director\ownership-matrix.md'
    'docs\phase-3-architecture.md'
    'docs\data-lifecycle.md'
    'docs\security-and-privacy.md'
    'pyproject.toml'
)
$requiredSchemas = @(
    'authorization-manifest'
    'ingestion-manifest'
    'project-intake'
    'specialist-brief'
    'specialist-finding'
    'keyword-cluster'
    'technical-issue'
    'content-action'
    'backlink-prospect'
    'cro-hypothesis'
    'measurement-kpi'
    'implementation-qa-result'
    'monitoring-event'
)

foreach ($requiredSkill in @($requiredCoreSkills + $specialistSkills)) {
    $requiredSkillFile = Join-Path $skillsRoot "$requiredSkill\SKILL.md"
    if (-not (Test-Path -LiteralPath $requiredSkillFile -PathType Leaf)) {
        $errors.Add("Missing required skill: $requiredSkillFile")
    }
}

foreach ($relativePath in $requiredControlFiles) {
    $requiredPath = Join-Path $repositoryRoot $relativePath
    if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) {
        $errors.Add("Missing Phase 3 control file: $requiredPath")
    }
}

foreach ($schemaName in $requiredSchemas) {
    $schemaFile = Join-Path $repositoryRoot "schemas\$schemaName.schema.json"
    if (-not (Test-Path -LiteralPath $schemaFile -PathType Leaf)) {
        $errors.Add("Missing machine-readable schema: $schemaFile")
        continue
    }
    try {
        $schema = Get-Content -LiteralPath $schemaFile -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($schema.'$schema' -ne 'https://json-schema.org/draft/2020-12/schema') {
            $errors.Add("Schema does not declare JSON Schema 2020-12: $schemaFile")
        }
        if ($schema.type -ne 'object') {
            $errors.Add("Schema root must be an object: $schemaFile")
        }
    } catch {
        $errors.Add("Invalid JSON schema: $schemaFile ($($_.Exception.Message))")
    }
}

$requiredBatch2Paths = @(
    'src\seo_os\authorization.py'
    'src\seo_os\datasets.py'
    'src\seo_os\secrets.py'
    'src\seo_os\cli.py'
    'src\seo_os\connectors\managed.py'
    'src\seo_os\connectors\transport.py'
    'src\seo_os\connectors\gsc.py'
    'src\seo_os\connectors\ga4.py'
    'src\seo_os\connectors\ahrefs.py'
    'src\seo_os\connectors\pagespeed.py'
    'src\seo_os\connectors\crux.py'
    'src\seo_os\connectors\tabular.py'
    'src\seo_os\ingestion\pipeline.py'
)
foreach ($relativePath in $requiredBatch2Paths) {
    $requiredPath = Join-Path $repositoryRoot $relativePath
    if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) {
        $errors.Add("Missing Phase 3 Batch 2 implementation: $requiredPath")
    }
}

$requiredBatch3Paths = @(
    'src\seo_os\procedures\common.py'
    'src\seo_os\procedures\framework.py'
    'src\seo_os\procedures\ownership.py'
    'src\seo_os\procedures\technical.py'
    'src\seo_os\procedures\serp.py'
    'src\seo_os\procedures\keyword.py'
    'src\seo_os\procedures\content.py'
    'src\seo_os\procedures\geo.py'
    'src\seo_os\procedures\authority.py'
    'src\seo_os\procedures\cro.py'
    'src\seo_os\procedures\measurement.py'
)
foreach ($relativePath in $requiredBatch3Paths) {
    $requiredPath = Join-Path $repositoryRoot $relativePath
    if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) {
        $errors.Add("Missing Phase 3 Batch 3 implementation: $requiredPath")
    }
}

$forbiddenLaterBatchPaths = @(
    '.agents\skills\ecommerce-seo\SKILL.md'
    '.agents\skills\seo-implementation-qa\SKILL.md'
    'src\seo_os\monitoring'
    'src\seo_os\connectors\shopify.py'
    'src\seo_os\connectors\merchant_center.py'
    'src\seo_os\connectors\bing.py'
    'src\seo_os\connectors\google_business_profile.py'
    'src\seo_os\connectors\screaming_frog.py'
    'src\seo_os\connectors\crm.py'
    'src\seo_os\connectors\rank_tracker.py'
    'src\seo_os\scheduling'
)
foreach ($relativePath in $forbiddenLaterBatchPaths) {
    $forbiddenPath = Join-Path $repositoryRoot $relativePath
    if (Test-Path -LiteralPath $forbiddenPath) {
        $errors.Add("Later-batch implementation is present in Batch 3: $forbiddenPath")
    }
}

foreach ($skillFile in $skillFiles) {
    if ($skillFile.Length -eq 0) {
        $errors.Add("Zero-byte skill: $($skillFile.FullName)")
        continue
    }

    $content = Get-Content -LiteralPath $skillFile.FullName -Raw -Encoding UTF8
    $frontmatter = [regex]::Match(
        $content,
        '(?s)\A---\r?\nname:\s*([^\r\n]+)\r?\ndescription:\s*([^\r\n]+)\r?\n---\r?\n'
    )

    if (-not $frontmatter.Success) {
        $errors.Add("Invalid YAML frontmatter: $($skillFile.FullName)")
        continue
    }

    $name = $frontmatter.Groups[1].Value.Trim()
    $description = $frontmatter.Groups[2].Value.Trim()

    if ($name -ne $skillFile.Directory.Name) {
        $errors.Add("Skill name '$name' does not match folder '$($skillFile.Directory.Name)'")
    }
    if ($name -notmatch '^[a-z0-9-]{1,63}$') {
        $errors.Add("Invalid skill name '$name'")
    }
    if ([string]::IsNullOrWhiteSpace($description)) {
        $errors.Add("Empty description: $($skillFile.FullName)")
    }
}

foreach ($specialistSkill in $specialistSkills) {
    $specialistSkillFile = Join-Path $skillsRoot "$specialistSkill\SKILL.md"
    if (Test-Path -LiteralPath $specialistSkillFile -PathType Leaf) {
        $content = Get-Content -LiteralPath $specialistSkillFile -Raw -Encoding UTF8
        if ($content -notmatch [regex]::Escape('../seo-director/specialist-contract.md')) {
            $errors.Add("Specialist does not inherit the delegation contract: $specialistSkillFile")
        }
        if ($content -notmatch 'Use\s+`[A-Z]+-##`\s+IDs') {
            $errors.Add("Specialist has no stable workstream ID rule: $specialistSkillFile")
        }
        if ($content -notmatch [regex]::Escape('references/procedure.md')) {
            $errors.Add("Specialist does not reference its deterministic procedure: $specialistSkillFile")
        }
        $procedureFile = Join-Path $skillsRoot "$specialistSkill\references\procedure.md"
        if (-not (Test-Path -LiteralPath $procedureFile -PathType Leaf)) {
            $errors.Add("Specialist deterministic procedure is missing: $procedureFile")
        }
    }
}

$intakeSkillFile = Join-Path $skillsRoot 'project-intake\SKILL.md'
if (Test-Path -LiteralPath $intakeSkillFile -PathType Leaf) {
    $intakeContent = Get-Content -LiteralPath $intakeSkillFile -Raw -Encoding UTF8
    if ($intakeContent -match 'Likely specialist skills:') {
        $errors.Add("Project Intake is selecting specialist skills: $intakeSkillFile")
    }
    if ($intakeContent -notmatch 'Do not recommend or select specialist skills') {
        $errors.Add("Project Intake has no explicit routing boundary: $intakeSkillFile")
    }
}

$blueprintTemplateFile = Join-Path $skillsRoot 'seo-growth-blueprint\templates.md'
if (Test-Path -LiteralPath $blueprintTemplateFile -PathType Leaf) {
    $blueprintTemplate = Get-Content -LiteralPath $blueprintTemplateFile -Raw -Encoding UTF8
    if ($blueprintTemplate -match 'Score\s+0.{1,3}100') {
        $errors.Add("Blueprint template still creates unsupported numeric domain scores: $blueprintTemplateFile")
    }
}

$directorRoot = Join-Path $skillsRoot 'seo-director'
$googleRequirementsFile = Join-Path $directorRoot 'google-search-requirements.md'
if (-not (Test-Path -LiteralPath $googleRequirementsFile -PathType Leaf)) {
    $errors.Add("Missing Google requirements baseline: $googleRequirementsFile")
} else {
    $googleRequirements = Get-Content -LiteralPath $googleRequirementsFile -Raw -Encoding UTF8
    if ($googleRequirements -notmatch 'Last verified against official Google documentation:\s*\d{4}-\d{2}-\d{2}') {
        $errors.Add("Google requirements baseline has no valid verification date: $googleRequirementsFile")
    }

    foreach ($link in [regex]::Matches($googleRequirements, '\]\((https?://[^)]+)\)')) {
        $url = [uri]$link.Groups[1].Value
        if ($url.Scheme -ne 'https') {
            $errors.Add("Non-HTTPS Google reference: $($url.AbsoluteUri)")
        }
        if ($url.Host -notin @('developers.google.com', 'support.google.com')) {
            $errors.Add("Non-official domain in Google requirements baseline: $($url.AbsoluteUri)")
        }
    }
}

$directorSkillFile = Join-Path $directorRoot 'SKILL.md'
$specialistContractFile = Join-Path $directorRoot 'specialist-contract.md'
foreach ($requiredReferenceFile in @($directorSkillFile, $specialistContractFile)) {
    if (Test-Path -LiteralPath $requiredReferenceFile -PathType Leaf) {
        $content = Get-Content -LiteralPath $requiredReferenceFile -Raw -Encoding UTF8
        if ($content -notmatch [regex]::Escape('google-search-requirements.md')) {
            $errors.Add("Google requirements baseline is not referenced by: $requiredReferenceFile")
        }
    }
}

$markdownFiles = @(
    Get-ChildItem -LiteralPath (Join-Path $repositoryRoot '.agents') -Filter '*.md' -File -Recurse
    Get-Item -LiteralPath (Join-Path $repositoryRoot 'AGENTS.md')
    Get-Item -LiteralPath (Join-Path $repositoryRoot 'README.md')
    if (Test-Path -LiteralPath (Join-Path $repositoryRoot 'docs')) {
        Get-ChildItem -LiteralPath (Join-Path $repositoryRoot 'docs') -Filter '*.md' -File -Recurse
    }
)
foreach ($markdownFile in $markdownFiles) {
    $content = Get-Content -LiteralPath $markdownFile.FullName -Raw -Encoding UTF8
    foreach ($match in [regex]::Matches($content, '`([^`\r\n]+\.md)`')) {
        $reference = $match.Groups[1].Value
        if ($reference -match 'YYYY|<[^>]+>|\*|^https?://' ) {
            continue
        }

        if ($reference -match '^\.agents[/\\]' -or $reference -in @('AGENTS.md', 'README.md')) {
            $candidate = Join-Path $repositoryRoot $reference
        } else {
            $candidate = Join-Path $markdownFile.Directory.FullName $reference
        }

        $resolved = [System.IO.Path]::GetFullPath($candidate)
        if (-not $resolved.StartsWith($repositoryRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
            $errors.Add("Reference escapes repository: $($markdownFile.FullName) -> $reference")
        } elseif (-not (Test-Path -LiteralPath $resolved -PathType Leaf)) {
            $errors.Add("Broken Markdown reference: $($markdownFile.FullName) -> $reference")
        }
    }
}

$legacyMatches = $markdownFiles | Select-String -SimpleMatch 'legacy-seo-growth-blueprint'

if ($legacyMatches) {
    foreach ($legacyMatch in $legacyMatches) {
        $errors.Add("Legacy skill reference: $($legacyMatch.Path):$($legacyMatch.LineNumber)")
    }
}

$obsoletePromptsFile = Join-Path $skillsRoot 'seo-growth-blueprint\prompts.md'
if (Test-Path -LiteralPath $obsoletePromptsFile) {
    $errors.Add("Obsolete blueprint prompt file still exists: $obsoletePromptsFile")
}

if ($errors.Count -gt 0) {
    $errors | ForEach-Object { Write-Error $_ }
    exit 1
}

$privacyScript = Join-Path $repositoryRoot 'scripts\check-privacy.ps1'
if (-not (Test-Path -LiteralPath $privacyScript -PathType Leaf)) {
    Write-Error "Missing privacy validation script: $privacyScript"
    exit 1
}
& $privacyScript -Mode Workspace
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

function Resolve-PythonInterpreter {
    param([string]$RequestedPath)

    foreach ($candidate in @($RequestedPath, $env:SEO_OS_PYTHON, 'python', 'python3')) {
        if ([string]::IsNullOrWhiteSpace($candidate)) {
            continue
        }
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
        $command = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($command) {
            return $command.Source
        }
    }
    return $null
}

$python = Resolve-PythonInterpreter -RequestedPath $PythonPath
if ($python) {
    $previousPythonPath = $env:PYTHONPATH
    $previousDontWriteBytecode = $env:PYTHONDONTWRITEBYTECODE
    try {
        $sourceRoot = Join-Path $repositoryRoot 'src'
        $env:PYTHONDONTWRITEBYTECODE = '1'
        $env:PYTHONPATH = if ($previousPythonPath) {
            "$sourceRoot$([System.IO.Path]::PathSeparator)$previousPythonPath"
        } else {
            $sourceRoot
        }
        & $python -m unittest discover -s (Join-Path $repositoryRoot 'tests') -v
        if ($LASTEXITCODE -ne 0) {
            exit $LASTEXITCODE
        }
    } finally {
        $env:PYTHONPATH = $previousPythonPath
        $env:PYTHONDONTWRITEBYTECODE = $previousDontWriteBytecode
    }
} elseif ($RequirePython) {
    Write-Error 'Python 3.11 or newer is required for Phase 3 contract validation.'
    exit 1
} else {
    Write-Warning 'Python was not found; Phase 3 Python tests were skipped. Use -RequirePython in CI.'
}

Write-Output "Validated $($skillFiles.Count) skills, $($markdownFiles.Count) agent Markdown files, and $($requiredSchemas.Count) Phase 3 schemas."
