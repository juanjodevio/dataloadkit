# Spec planning (`spec/`)

Each **spec** is a folder: **`spec/<spec_name>/`**. Use **kebab-case** for `spec_name`. In Cursor, reference the folder with **`@spec`**.

## Contents

| Path | Purpose |
|------|--------|
| `DESIGN.md` | Technical design **first**—bounds the solution (aligned with `STRUCTURE.md` / `TECH.md`). |
| `REQUIREMENTS.md` | **[EARS](https://alistairmavin.com/ears/)** where applicable, plus **acceptance criteria** (spec-level, usually in the traceability table—what is verifiably true when requirements are met). |
| `tasks/1_<task>.plan.md` … `tasks/N_<task>.plan.md` | Ordered, actionable task plans; each maps to Git branch **`spec_name/task-slug`** and declares **`depends_on_tasks`**. |

**Authoring order:** **`DESIGN.md` → `REQUIREMENTS.md` → `tasks/*.plan.md`**. Do not write EARS requirements before design is drafted unless explicitly waived.

**Git:** one branch per task plan, name **`{spec_name}/{task-slug}`** (see plan frontmatter **`git_branch`**). Validate inter-task dependencies (no cycles, no orphan slugs)—see **spec-planning-enforcer**.

## Copy templates

Duplicate **`_template/`** to **`spec/<your-spec-name>/`** (include the **`tasks/`** folder), then edit placeholders.

See **`.cursor/rules/spec-planning-enforcer.mdc`** for enforcement rules, missing-file protocol, and creation **order**.
