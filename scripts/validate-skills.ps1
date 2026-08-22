[CmdletBinding()]
param()

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

foreach ($requiredSkill in @($requiredCoreSkills + $specialistSkills)) {
    $requiredSkillFile = Join-Path $skillsRoot "$requiredSkill\SKILL.md"
    if (-not (Test-Path -LiteralPath $requiredSkillFile -PathType Leaf)) {
        $errors.Add("Missing required skill: $requiredSkillFile")
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

Write-Output "Validated $($skillFiles.Count) skills and $($markdownFiles.Count) agent Markdown files."
