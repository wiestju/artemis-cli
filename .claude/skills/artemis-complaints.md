# Artemis Complaints — Review and Respond to Student Complaints

You help tutors handle grade complaints and more-feedback requests on Artemis efficiently.
Discover exercise IDs from the CLI — never ask for something the tool can look up.

## Workflow

### 1. Find the exercise

If the user gives a course or exercise name instead of an ID:

```bash
artemis courses list
artemis courses exercises <course_id>
```

Match the exercise and note its `exercise_id`.

### 2. List open complaints

```bash
artemis complaints list <exercise_id>
artemis complaints feedback-list <exercise_id>
```

Show a summary table:

```text
ID     Type              Student   Submitted          Score  Complaint
─────────────────────────────────────────────────────────────────────
1042   COMPLAINT         u12345    2 days ago         6/10   "The deduction for X is unfair"
1055   MORE_FEEDBACK     u67890    5 hours ago        8/10   "Could you explain feedback #2?"
```

If there are no open items, say so and stop.

### 3. Work through complaints one by one

For each complaint, ask the user which one to handle next (by ID), or process in order.

For each:
1. Show the original complaint text and the assessment that triggered it
2. Ask: "What is your response?" (or offer a default: "Thank you for your feedback. After review...")
3. Ask: "Accept the grade change / Reject / More info needed?"

Then submit:

```bash
artemis complaints respond <complaint_id> --text "<response>" --accept   # or --reject
```

### 4. Handle locked complaints

If a complaint is locked by another tutor:

```bash
artemis complaints unlock <complaint_id>
```

Only do this if the user explicitly asks — do not unlock without confirmation.

### 5. Summary

After handling all complaints, show a final count:
- Accepted (grade changed)
- Rejected
- Remaining open

## Behaviour rules

- Never unlock a complaint without explicit user confirmation.
- Always show the original complaint text before asking for a response.
- Discover all IDs from the CLI — only ask the user if truly unavailable.
- If the user says "handle all complaints for course X", list all exercises in that course
  and check each one for open complaints.
