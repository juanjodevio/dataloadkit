---
status: TODO
git_branch: <spec_name>/<task-slug>
task_slug: <task-slug>
depends_on_tasks: []
blocks_tasks: []
---

# Task: <task name>

## Objective
What does this task accomplish?

## Scope
What is included in this task?

## Out of Scope
What is explicitly excluded from this task?

## Related Spec
- Spec: `spec/<spec_name>/`
- Design: `spec/<spec_name>/DESIGN.md`
- Requirements: `spec/<spec_name>/REQUIREMENTS.md`

## Dependencies
**Frontmatter (required by `.cursor/rules/spec-planning-enforcer.mdc`):** `git_branch` = `spec_name/task-slug` (matches this file’s `N_<task-slug>.plan.md`), `task_slug` = same `<task-slug>`, `depends_on_tasks` = list of upstream **task slugs** in this spec, `blocks_tasks` = optional downstream slugs.

List what must exist before this task can start.

Examples:
- upstream task completed
- interface agreed
- schema created
- API contract finalized

## Blocks
List which downstream tasks depend on this task.

## Parallelization Assessment

### Classification
Choose one:
- Sequential
- Parallel after interface agreement
- Fully parallel
- Conflict-prone

### Reasoning
Explain why this task can or cannot run in parallel.

### Coordination Notes
Describe shared contracts, sequencing, mocks, merge risks, or ownership boundaries.

## Affected Files / Modules
List the files, modules, services, routes, components, tables, or jobs likely affected.

## Inputs
What inputs, artifacts, or decisions does this task rely on?

## Expected Outputs
What concrete output should exist when this task is done?

Examples:
- endpoint implemented
- schema created
- UI flow completed
- tests added
- docs updated

## Implementation Approach
Describe the intended implementation steps.

Keep this practical and execution-oriented.

## Validation
How should this task be validated?

### Automated Validation
Examples:
- unit tests
- integration tests
- e2e tests
- lint
- typecheck
- migrations

### Manual Validation
Examples:
- UI walkthrough
- API verification
- happy path test
- edge case test

## Done Criteria
What must be true before this task can be marked `DONE`?

Examples:
- implementation complete
- tests added or updated
- validation passed
- docs updated if needed
- no unresolved blocker remains

## Blockers
List any current blockers if status is `BLOCKED`.

## Notes
Any additional implementation notes, assumptions, or follow-up observations.
