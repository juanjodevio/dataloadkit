# Cursor spec-driven template

> A minimal **documentation-first** starter for software projects: root specs, per-feature folders under `spec/`, and Cursor rules that push **design → EARS requirements → task plans** before implementation.

Use this repo as a **GitHub template**, or copy the files into a new project and replace the bracketed placeholders in the root docs.

## Quick start

1. **Clone or generate** a new repo from this template.
2. **Fill the root docs** (in order): [`PRODUCT.md`](PRODUCT.md) → [`STRUCTURE.md`](STRUCTURE.md) → [`TECH.md`](TECH.md). Each file is a template with placeholders.
3. **Add a feature spec**: copy [`spec/_template/`](spec/_template) to `spec/<your-spec-name>/` (kebab-case), then edit `DESIGN.md`, `REQUIREMENTS.md`, and add plans under `tasks/`. See [`spec/README.md`](spec/README.md).
4. **Open the repo in Cursor** so `.cursor/rules/` apply. Use **`@spec`** to attach a spec folder in chat.

## What lives where

| Document | Role |
|----------|------|
| [`PRODUCT.md`](PRODUCT.md) | Product intent, scope, MVP, risks |
| [`STRUCTURE.md`](STRUCTURE.md) | Repo layout, module boundaries, ownership |
| [`TECH.md`](TECH.md) | Stack, ADRs, security, NFRs, tooling |
| [`spec/<spec_name>/`](spec/README.md) | Per feature: `DESIGN.md` → `REQUIREMENTS.md` (EARS) → `tasks/N_<slug>.plan.md` |

Task plans map to Git branches **`spec_name/task-slug`** and declare **`depends_on_tasks`** for ordering PRs. Details are in [`.cursor/rules/spec-planning-enforcer.mdc`](.cursor/rules/spec-planning-enforcer.mdc).

## Cursor

| Path | Purpose |
|------|---------|
| [`.cursor/rules/spec-driven-enforcer.mdc`](.cursor/rules/spec-driven-enforcer.mdc) | Spec-before-code; missing root/spec file protocol |
| [`.cursor/rules/spec-planning-enforcer.mdc`](.cursor/rules/spec-planning-enforcer.mdc) | `spec/` layout, EARS, tasks, branches, dependency graph |
| [`.cursor/rules/technical-writer.mdc`](.cursor/rules/technical-writer.mdc) | Markdown / docs tone (applies to `**/*.md`) |
| [`.cursor/BUGBOT.md`](.cursor/BUGBOT.md) | Context for [Cursor Bugbot](https://cursor.com/docs/bugbot) PR reviews (enable in the [dashboard](https://cursor.com/dashboard/integrations)) |

## Optional extras

- **`docs/decisions/`** — ADRs if you use them (see `STRUCTURE.md`).
- **`cursor-rules-archive/`** — Archived agent rules; not loaded by Cursor unless you move files back into `.cursor/rules/`.

## License

[Add your license here, or remove this section.]
