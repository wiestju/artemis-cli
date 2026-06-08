# Artemis Score — Personal Grade Overview

You give students a full overview of their scores and results across all Artemis courses
and exercises. Discover everything from the CLI without asking the user for IDs.

## Workflow

### 1. List all courses

```bash
artemis courses list
```

Note all `course_id` values.

### 2. List exercises per course

For each course:

```bash
artemis courses exercises <course_id>
```

Collect `exercise_id`, `title`, `maxPoints`, `dueDate`, and `type` for each exercise.

### 3. Fetch results

For exercises where the user has a known `participation_id`, run:

```bash
artemis submissions result <participation_id>
```

If the user does not know their participation IDs, note which exercises are missing results
and ask if they want to look them up manually in the Artemis web UI.

### 4. Calculate and display

Build a per-course summary:

```text
── Algorithmen II ──────────────────────────────────────────────────
  Sheet 01 — Lists           8.5 / 10.0   85%  ✓
  Sheet 02 — Trees           6.0 / 10.0   60%  ✓
  Sheet 03 — Graphs          9.0 / 10.0   90%  ✓
  Sheet 04 — Sorting         —            —    not submitted
  ─────────────────────────────────────────────
  Course total               23.5 / 30.0  78%

── Softwaretechnik ─────────────────────────────────────────────────
  ...
```

At the bottom, show an overall average across all courses with results.

### 5. Highlight weak spots

If any exercise scored below 50%, mark it clearly and offer to show the full feedback:

```bash
artemis submissions result <participation_id>
```

## Behaviour rules

- Discover all course and exercise IDs from the CLI — never ask for them upfront.
- Missing results (no submission or no grading yet) should be shown as `—` not omitted.
- If the user says "only show course X", filter accordingly.
- Do not calculate scores for exercises that are not yet due.
