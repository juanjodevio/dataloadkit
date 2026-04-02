---
status: DRAFT
---

# Requirements

## Purpose
Briefly describe what this feature or spec is intended to achieve.

## Scope
What is included in this feature?

## Out of Scope
What is explicitly excluded?

## Actors
Who interacts with this feature?

Examples:
- Doctor
- Patient
- Admin
- External system

## Preconditions
What must already be true before this feature can work?

Examples:
- User is authenticated
- Patient record exists
- Appointment exists
- Required integration is configured

## Functional Requirements

Use EARS where it improves clarity and testability.

### Ubiquitous Requirements
Use for statements that are always true.

Examples:
- The system shall store each consultation with a creation timestamp.
- The system shall associate each consultation with exactly one patient.
- The system shall preserve the final saved note as the source of truth.

### Event-Driven Requirements
Use when something happens in response to a trigger.

Format:
- When <trigger>, the system shall <response>.

Examples:
- When a doctor uploads consultation audio, the system shall store the audio and start transcription.
- When a doctor saves a consultation note, the system shall persist the edited note and update consultation history.
- When a task is completed, the system shall update its status to DONE.

### Conditional Requirements
Use when behavior depends on a condition.

Format:
- If <condition>, the system shall <response>.

Examples:
- If transcription fails, the system shall mark the consultation as transcription_failed and show an error state.
- If a required upstream spec artifact is missing, the system shall stop task creation and request the missing artifact first.
- If a task plan is already marked DONE, the system shall not regenerate it unless explicitly reopened.

### State-Driven Requirements
Use when behavior applies only while the system is in a certain state.

Format:
- While <state>, the system shall <response>.

Examples:
- While note generation is in progress, the system shall show the consultation as processing.
- While a task is marked IN_PROGRESS, the system shall preserve its assigned branch and dependencies.
- While a record is locked for editing, the system shall prevent concurrent updates.

### Optional / Feature-Scoped Requirements
Use when a behavior only applies in a specific context or variant.

Format:
- Where <feature/context applies>, the system shall <response>.

Examples:
- Where audio recording is supported, the system shall allow the doctor to start and stop recording from the consultation screen.
- Where multi-doctor clinics are enabled, the system shall scope access according to clinic membership.
- Where a task is parallelizable, the system shall assign it a dedicated branch using the format `{spec}/{task}`.

## Data Requirements
What data must be created, read, updated, or preserved?

Examples:
- Required fields
- Ownership constraints
- Retention expectations
- Status fields
- Audit fields

## Interface / Contract Requirements
What external or internal contracts must be honored?

Examples:
- API payload requirements
- Validation rules
- Event contracts
- File format requirements
- UI state requirements

## Non-Functional Requirements

### Performance
Examples:
- The system shall return the consultation detail view in under 2 seconds under normal load.
- The system shall generate an AI draft note within 30 seconds for supported audio lengths.

### Reliability
Examples:
- The system shall not lose uploaded consultation audio after a successful upload response.
- The system shall preserve status and branch metadata for each task plan.

### Security / Privacy
Examples:
- The system shall restrict access so a doctor can only view their own patients in MVP.
- The system shall store secrets outside the codebase.
- The system shall audit note creation and edits.

### Usability
Examples:
- The system shall be usable on mobile web for core doctor workflows.
- The system shall allow a doctor to review and edit AI-generated notes before final save.

### Observability
Examples:
- The system shall emit structured logs for note generation failures.
- The system shall record task lifecycle changes for spec-driven workflows.

## Acceptance Criteria
List the concrete outcomes that must be true for this feature to be considered complete.

Examples:
- A doctor can create a consultation and save a final note.
- A doctor can upload audio and receive a draft SOAP note.
- A completed task is marked DONE and is not regenerated automatically.
- A task plan includes dependencies, parallelization assessment, and branch name.

## Edge Cases
List tricky or failure scenarios.

Examples:
- Empty or corrupted audio file
- Doctor cancels mid-process
- Duplicate patient names
- Task file exists but has invalid metadata
- Dependency task is BLOCKED
- Required spec file exists but is incomplete

## Assumptions
List assumptions currently being made.

## Open Questions
List unresolved points that must be answered later.

## Notes
Anything important that does not fit above.