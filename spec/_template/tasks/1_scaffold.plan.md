---
status: DRAFT
spec_name: "[spec-name]"
plan: 1
task_slug: "[task-slug]"
git_branch: "[spec_name]/[task-slug]"
depends_on_tasks: []
blocks_tasks: []
path: "spec/<spec_name>/tasks/"
---

# Plan: [Short title — e.g. scaffold project layout]

## Git branch

**Convention:** work on a branch named exactly **`{spec_name}/{task-slug}`** (one slash), where:

- **`spec_name`** is the folder `spec/<spec_name>/` (kebab-case).
- **`task_slug`** matches this file’s name: `N_<task-slug>.plan.md` (same slug, no `N_` prefix).

Example: spec `patient-import`, file `1_add-migration.plan.md` → branch **`patient-import/add-migration`**.

- [ ] Branch created from the agreed base (e.g. `main`).
- [ ] PR targets the same base; branch name matches `git_branch` in frontmatter.

## Goal

[One paragraph: what this plan delivers.]

## Definition of done

- [ ] [Verifiable outcome 1]
- [ ] [Verifiable outcome 2]

## Inter-task dependencies

Fill **`depends_on_tasks`** in YAML with **task slugs** (not plan numbers) in **this spec** that must be **merged before** this task’s branch merges. Leave empty if none.

| Dependency (task slug) | Branch that must land first | Notes |
|------------------------|-----------------------------|------|
| [e.g. `add-migration`] | `spec_name/add-migration` | |

**Blocks (optional):** list task slugs that should not start until this lands → use **`blocks_tasks`** in frontmatter or a row here.

## Out of scope (this plan)

- [What we are not doing in this file]

## Steps

Execute in order unless marked parallel.

- [ ] **Step 1:** [Concrete action—e.g. create `apps-api` skeleton per STRUCTURE.md]
- [ ] **Step 2:** […]
- [ ] **Step 3:** […]

## Other dependencies

- **Requires:** [`DESIGN.md` / `REQUIREMENTS.md`; env vars; feature flags]
- **External:** [tickets, services]

## Notes

[Risks, links to tickets, rollout order]
