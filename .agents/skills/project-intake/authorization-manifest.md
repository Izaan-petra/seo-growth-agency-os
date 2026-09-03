# Authorization Manifest Control

`project-intake` owns creation and maintenance of the authorization manifest. The manifest records what the user authorized, not authentication credentials themselves.

Validate machine-readable manifests against `../../../schemas/authorization-manifest.schema.json`.

## Required behavior

1. Create an authorization record only after the source, purpose, resource, acquisition method, fields, date scope, and intended consumers are known.
2. Use a separate connector entry when purpose or authorized resources differ.
3. Set `access_mode` to `read-only`. No SEO OS connector has a write-capable contract.
4. Store only an environment-variable name or managed-secret reference in `credential_reference`.
5. Never store a password, token, cookie, MFA code, recovery code, private key, service-account JSON, or OAuth response in the manifest.
6. Mark authorization `expired` or `revoked` when it can no longer be reused.
7. Return to Project Intake when a workflow needs a new provider, property, field, purpose, scope, or materially wider date range.
8. An available connector is not authorization. Both availability and authorized scope must be confirmed.
9. Add `allowed_record_types` for every executable Batch 2 grant. This is the operation allowlist; connector execution fails closed when it is absent or does not contain the requested record type.

## Safe example

```json
{
  "schema_version": "1.0.0",
  "authorization_id": "AUTHZ-DEMO-001",
  "project_id": "PROJECT-DEMO",
  "status": "active",
  "created_at": "2026-09-02T10:00:00Z",
  "expires_at": null,
  "authorized_by_reference": "client-approval-record",
  "connectors": [
    {
      "connector_id": "ahrefs-read-demo",
      "provider": "ahrefs",
      "purpose": "Approved backlink baseline",
      "authentication_method": "environment-secret",
      "credential_reference": "AHREFS_API_KEY",
      "acquisition_methods": ["api", "export"],
      "access_mode": "read-only",
      "resource_ids": ["example.com"],
      "allowed_fields": ["url_from", "url_to", "root_name_source", "first_seen"],
      "allowed_record_types": ["ahrefs-backlinks"],
      "start_date": null,
      "end_date": null,
      "limitations": ["Ahrefs values are third-party estimates"]
    }
  ],
  "data_minimization": {
    "purpose_limited": true,
    "pii_allowed": false,
    "retention_policy": "docs/data-lifecycle.md default"
  }
}
```

The example shows a credential reference only. It does not prove that the secret is available, the account can use the endpoint, or the target is accessible.

## Handoff

Include the authorization manifest ID in the machine-readable project intake. Specialists receive evidence references through the director brief; they do not receive credentials, authorization tokens, or permission to broaden collection.
