# Bugbot — project review context

Use this file so [Cursor Bugbot](https://cursor.com/docs/bugbot) reviews align with this repository’s spec-driven template.

## Enable Bugbot (dashboard)

Bugbot runs on pull requests after you connect GitHub in the [Cursor dashboard](https://cursor.com/dashboard/integrations) and turn on Bugbot for this repo. Repo files here **do not** replace that step— they only add review context.

## Review priorities

1. **Correctness and regressions** — logic errors, broken edge cases, race-prone async, incorrect error handling.
2. **Security** — injection, authz bypasses, secret leakage, unsafe deserialization, dangerous dynamic execution.
3. **Spec alignment** — when `PRODUCT.md`, `STRUCTURE.md`, `TECH.md`, or `spec/<spec_name>/` (`DESIGN.md`, EARS `REQUIREMENTS.md`, `tasks/*.plan.md`) define behavior, flag likely **drift** (implementation contradicts documented intent without an accompanying doc or ADR update).
4. **Sensitive data** — avoid logging or exposing PII/PHI/secrets; ensure redaction and least-privilege access patterns match `TECH.md` when present.

## Tone and noise

- Prefer **actionable** comments on the diff; avoid nitpicks that duplicate the linter unless they catch a real bug.
- If suggesting a change, note **why** (bug risk, security, or spec mismatch)—not style alone when formatters cover it.

## Manual triggers

Reviewers can comment `cursor review` or `bugbot run` on a PR to trigger Bugbot per [Cursor docs](https://cursor.com/docs/bugbot).
