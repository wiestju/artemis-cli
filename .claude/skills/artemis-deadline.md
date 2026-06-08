# Artemis Deadlines — Upcoming Submission Deadlines

You help students and tutors get a clear overview of upcoming exercise deadlines across
all their Artemis courses. When invoked, discover everything from the CLI — never ask
for IDs the tool can find itself.

## Workflow

### 1. List all courses

```bash
artemis courses list
```

Note every `course_id` from the output.

### 2. List exercises per course

For each course:

```bash
artemis courses exercises <course_id>
```

Collect all exercises with their `dueDate`, `title`, and `id`.

### 3. Filter and sort

- Keep only exercises where `dueDate` is in the future (within the next 14 days by default)
- Sort ascending by `dueDate`
- Mark exercises due within 48 hours as urgent

### 4. Display

Show a clean table:

```text
Course          Exercise                      Due                  Status
──────────────────────────────────────────────────────────────────────────
Algo II         Sheet 07 — Graphs             tomorrow 23:59       ⚠ urgent
Softwaretech    UML Class Diagram             in 3 days            open
Algo II         Sheet 08 — Sorting            in 8 days            open
```

If the user asks about a specific course or time window, filter accordingly.

### 5. Optional: check submission status

If the user wants to know which exercises they already submitted, run:

```bash
artemis submissions result <participation_id>
```

for any exercise where they have a participation ID. Otherwise note that submission status
requires a participation ID.

## Behaviour rules

- Discover all course and exercise IDs automatically from the CLI.
- If `dueDate` is missing or null for an exercise, omit it from the deadline list.
- Never ask for IDs — collect them from `courses list` and `courses exercises`.
- If the user says "show me everything", extend the window to 30 days.
