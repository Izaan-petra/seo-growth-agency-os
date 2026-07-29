# Project Instructions

This repository contains the `seo-growth-blueprint` skill at:

`.agents/skills/seo-growth-blueprint/SKILL.md`

Use this skill whenever the user requests an SEO audit, SEO strategy, keyword/content plan, competitor analysis, GEO/AEO assessment, link-building campaign, or organic growth roadmap for a website.

Before substantial work, run the skill's data-source intake. Use `data-sources.md` to choose API, manual export, screenshot, or public mode; use `integrations.md` for secret handling; and use `data-access.md` for report-specific instructions. If API access is available, require an environment variable or cloud secret and never ask the user to paste a key into chat or commit it to Git. If authenticated data is available without API access, guide the user through safe exports using `data-access.md`. If it is not available, continue in public-data mode. Never request passwords, cookies, recovery codes, or other credentials.

Save final reports to `reports/` and source exports to `research/raw/` when the user asks for files.
