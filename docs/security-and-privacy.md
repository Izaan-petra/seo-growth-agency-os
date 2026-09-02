# Security and Privacy

## Credential rules

- Never request or store passwords, MFA codes, recovery codes, cookies or session material.
- Never ask a user to paste an API key or token into chat, Markdown, source code, reports or Git.
- Store provider credentials in environment variables, OS-managed credential storage or managed cloud secrets.
- Authorization manifests contain only variable names or managed-secret references.
- External integrations are read-only by default and in Batch 1 by enforced interface contract.
- A provider's broad OAuth scope does not authorize the runtime to call write operations.

## Authorization

Project Intake owns authorization records. Availability, authentication and authorization are separate states:

- **Available:** a tool or acquisition route exists.
- **Authenticated:** the runtime can establish provider identity.
- **Authorized:** the user approved a defined purpose, resource, field set and time range.

Collection requires all applicable states. A scheduled reuse is invalid after expiration, revocation, purpose change or scope expansion.

## Repository controls

- `.gitignore` excludes client, raw, processed, snapshot, cache, report and log artifacts by default.
- `.privacy-allowlist` contains the single pre-existing reviewed historical report exception. It does not permit new reports.
- `scripts/check-privacy.ps1` rejects staged or tracked client/generated artifacts outside explicit exceptions.
- The scanner checks high-confidence private-key, bearer-token, GitHub-token, AWS-key and credential-assignment patterns.
- `.gitleaks.toml` enables the standard Gitleaks rules and documents narrow synthetic/historical exceptions.
- `.pre-commit-config.yaml` runs staged privacy checks and the stable validation entry point.
- GitHub Actions runs with read-only repository permissions and pinned checkout code.

Repository scanning complements, but does not replace, GitHub secret scanning and push protection. Repository administrators should enable both where available.

## Safe logging

The Python logger redacts credential-like keys, bearer tokens, environment assignments, private-key blocks and email addresses. Connector errors must use non-sensitive categories such as authorization missing, resource not authorized, quota limit, provider outage or malformed export.

Never log:

- authorization headers
- access or refresh tokens
- cookies or session identifiers
- raw OAuth responses
- service-account JSON
- unredacted CRM/order/customer records
- uploaded client files or full provider response bodies

## Privacy validation

- Unknown fields in strict authorization and ingestion contracts fail validation.
- High-risk or unexpected data is quarantined rather than silently processed.
- CI uses synthetic fixtures only.
- Confidential ignored artifacts require local scanning because CI cannot see files that are never checked out.
- Sanitized artifacts require an explicit review decision before force-adding to Git.

## Incident response

If a possible secret is found:

1. Stop staging, committing and pushing.
2. Do not print the value while investigating.
3. Identify the provider and affected scope from non-sensitive metadata.
4. Revoke or rotate through the provider's secure interface.
5. Remove the value from the working tree and, if already committed, follow an approved history-remediation process.
6. Re-run privacy, secret and repository validation.
7. Record the incident without the credential value.
