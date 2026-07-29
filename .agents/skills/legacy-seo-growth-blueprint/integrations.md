# Integration and Secret-Handling Rules

## Local Codex or local development

Store API keys outside the repository as environment variables.

Example variable name:

```text
AHREFS_API_KEY
```

Do not place the value in:

- `SKILL.md`
- `AGENTS.md`
- `.env.example`
- committed `.env` files
- prompts
- reports
- screenshots
- issue trackers

A local `.env` file may be used only when it is excluded from Git. Ensure `.gitignore` contains:

```text
.env
.env.*
!.env.example
research/raw/*
!research/raw/.gitkeep
```

The example file may list variable names but must never contain real values.

## Codex Cloud

Configure provider credentials through the environment's secret-management interface. Use a clear name such as `AHREFS_API_KEY`.

Rules:

- Never commit the key to GitHub.
- Never paste the key into a task prompt.
- Never print the key to logs.
- Never copy it into a generated report.
- Use the secret only for the provider and task authorized by the user.
- If the environment cannot access the secret, switch to Manual Export or Screenshot mode.

## Connection confirmation

The agent may ask:

> Is the `AHREFS_API_KEY` secret configured in this environment?

The agent must not ask:

> What is your API key?

## API capability check

Before relying on an API:

1. Confirm the account is eligible for API access.
2. Confirm the user has permission to use the account for the target website.
3. Confirm the required report is available through the provider's current API.
4. Confirm date, country, domain/URL mode, limits, and requested fields.
5. Record data retrieval time and important limitations.
6. If the required data is not available through the API, request a manual export instead.

## Failure handling

If an API request fails:

- Do not reveal authorization headers or secret values.
- State the non-sensitive error category: unavailable secret, unauthorized, quota/rate limit, unsupported report, invalid target, or provider outage.
- Retry only when appropriate.
- Offer the exact manual export or screenshot fallback required for the task.

## Data retention

Treat client exports and API responses as confidential project data.

- Keep raw files in `research/raw/` only when needed.
- Keep processed files in `research/processed/`.
- Do not publish private exports in a public repository.
- Avoid storing unnecessary personal data.
- Remove or archive project data according to the user's policy.
