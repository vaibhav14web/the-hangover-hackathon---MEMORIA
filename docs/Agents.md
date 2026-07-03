# AGENTS.md

# Memoria – AI Institutional Memory Engine

> **Mission**
>
> Build Memoria exactly according to the PRD and SAD. Every implementation decision must be traceable to those documents. The AI agent is **not allowed** to invent features, modify architecture, or take shortcuts unless explicitly approved.

---

# 1. Core Principles

The agent MUST:

* Follow the PRD before writing any code.
* Follow the SAD before designing any module.
* Produce production-quality code.
* Produce deterministic code.
* Produce modular code.
* Produce maintainable code.
* Produce scalable code.
* Produce type-safe code.
* Produce documented code.

The agent MUST NOT:

* Hallucinate APIs.
* Hallucinate libraries.
* Hallucinate package names.
* Hallucinate SDK methods.
* Hallucinate return values.
* Hallucinate configuration keys.
* Hallucinate environment variables.

If uncertain,

**STOP**

verify from

* official documentation
* installed SDK
* source code
* existing project code

before continuing.

---

# 2. Single Source of Truth

Priority order:

1. User Instructions
2. PRD.md
3. SAD.md
4. Existing Project Code
5. Official Library Documentation
6. Community Documentation

If two sources conflict,

stop,

report the conflict,

ask for clarification.

Never silently choose one.

---

# 3. Architecture Compliance

Every implementation MUST respect the architecture.

```
React UI

↓

FastAPI

↓

Application Layer

↓

Domain Layer

↓

Memory Layer

↓

Cognee

↓

Groq

↓

Persistence
```

Never bypass layers.

Example:

❌ UI → Cognee

❌ UI → Database

✔ UI → API → Service → Cognee

---

# 4. Folder Ownership

Each folder has one responsibility.

```
api/
```

Only REST endpoints.

No business logic.

---

```
ingestion/
```

Only ingestion.

No retrieval.

No reasoning.

---

```
reasoning/
```

Only reasoning.

No GitHub logic.

---

```
graph/
```

Only graph construction.

---

```
retrieval/
```

Only retrieval.

---

```
storage/
```

Persistence only.

---

Never violate folder ownership.

---

# 5. Feature Development Workflow

Before implementing ANY feature:

Step 1

Understand requirement.

Step 2

Locate PRD requirement.

Step 3

Locate SAD architecture.

Step 4

Identify affected modules.

Step 5

Design interfaces.

Step 6

Implement.

Step 7

Run tests.

Step 8

Fix failures.

Step 9

Refactor.

Step 10

Verify against PRD.

---

# 6. Mandatory Engineering Process

Every task follows:

```
Understand

↓

Plan

↓

Design

↓

Implement

↓

Compile

↓

Test

↓

Debug

↓

Verify

↓

Document
```

Never skip steps.

---

# 7. Debugging Protocol

If any error occurs:

DO NOT GUESS.

Instead:

Collect stack trace.

↓

Identify failing module.

↓

Identify root cause.

↓

Propose fix.

↓

Implement.

↓

Run tests.

↓

Verify.

↓

Repeat if necessary.

Never change unrelated code.

Never apply speculative fixes.

---

# 8. Bounded Retry Policy

The agent should persist until the issue is resolved or a verified blocker is found.

Maximum retry attempts per root cause:

```
5
```

After every retry:

* Compare new error.
* Confirm progress.
* Record observations.

If the exact same error occurs five times:

STOP.

Generate a debugging report containing:

* Root cause investigated
* Attempts performed
* Logs
* Remaining blocker
* Suggested next actions

Never enter an infinite loop.

---

# 9. Zero Hallucination Policy

Never invent:

* SDK functions
* REST endpoints
* Models
* Classes
* Enums
* Search types
* Providers
* Configurations

If unsure:

Inspect.

Example:

```
dir(module)

help(module)

print(object)

read source

official docs
```

Evidence first.

Implementation second.

---

# 10. Code Quality Standards

Every file must satisfy:

PEP8

Type hints

Docstrings

Meaningful names

Dependency Injection

SOLID Principles

No duplicated logic

No dead code

No commented-out code

No magic numbers

No global mutable state

---

# 11. Error Handling

Never ignore exceptions.

Never swallow errors.

Use

```
try

↓

log

↓

recover

↓

raise if necessary
```

Every exception should include meaningful context.

---

# 12. Logging

Every major action logs:

Start

Success

Failure

Duration

Affected resource

Examples

```
Repository imported

PR ingestion completed

Graph built

Cognee retrieval completed

Reasoning completed
```

Never log secrets.

---

# 13. Performance Rules

Never perform:

Nested repository scans

Repeated API calls

Repeated embedding generation

Repeated graph construction

Always cache where appropriate.

Batch requests when possible.

Prefer async I/O.

---

# 14. GitHub Rules

Always:

Handle pagination.

Handle rate limits.

Retry transient failures.

Validate responses.

Support incremental updates.

Never assume repository structure.

---

# 15. Cognee Rules

Never call Cognee directly from UI.

All Cognee interactions belong in:

```
graph/

or

retrieval/
```

Always:

Validate response.

Handle retries.

Log failures.

Support incremental memory updates.

---

# 16. LLM Rules

Every prompt must:

Contain evidence.

Contain retrieved context.

Contain citations.

Never ask the LLM to invent missing information.

If evidence is insufficient:

Respond:

"I do not have enough evidence to answer confidently."

---

# 17. API Rules

Every endpoint:

Input validation

Output schema

HTTP status codes

Error responses

Logging

Timeout handling

Async implementation

---

# 18. Testing Requirements

Every completed feature must pass:

Unit Tests

Integration Tests

API Tests

Regression Tests

Performance Check

No feature is complete until tests pass.

---

# 19. Documentation Rules

Every module requires:

Purpose

Responsibilities

Dependencies

Inputs

Outputs

Example usage

---

# 20. Definition of Done

A task is complete only if:

✓ Matches PRD

✓ Matches SAD

✓ Builds successfully

✓ Passes linting

✓ Passes tests

✓ Has no known runtime errors

✓ Is documented

✓ No TODO placeholders

✓ No mock implementations

✓ No stub methods

✓ No fake data in production code

---

# 21. Forbidden Practices

Never:

* Ignore compiler errors
* Ignore warnings without reason
* Suppress exceptions
* Duplicate code
* Hardcode secrets
* Commit API keys
* Change architecture without approval
* Skip testing
* Skip verification
* Invent APIs
* Invent Cognee functionality

---

# 22. Continuous Verification

After every completed task:

1. Verify against PRD.
2. Verify against SAD.
3. Verify module boundaries.
4. Verify code quality.
5. Verify tests.
6. Verify runtime.
7. Verify documentation.

Only then continue to the next task.

---

# 23. Final Directive

The objective is **not to generate code quickly**.

The objective is to build a maintainable, production-quality AI Institutional Memory Engine that faithfully implements the Product Requirements Document and Software Architecture Document.

Every architectural decision must be justified.

Every feature must be traceable.

Every bug must be investigated before being fixed.

Every answer must be grounded in evidence.

**Quality, correctness, and architectural integrity always take precedence over speed.**
