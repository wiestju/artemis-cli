# artemis-cli

> Unofficial command-line interface for the [Artemis](https://github.com/ls1intum/Artemis) learning platform.

![CI](https://github.com/wiestju/artemis-cli/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-alpha-orange)

Works with any self-hosted Artemis instance — KIT, TUM, TU Darmstadt, and more.

---

## Features

- **Students** — browse courses and exercises, view problem statements
- **Tutors** — lock submissions, grade interactively, submit assessments, manage complaints
- **Instructors** — list and export submissions, submit external results
- **Secure auth** — JWT stored in system keyring; SSO (university login) supported via token paste
- **AI grading assistant** — Claude Code skill that fetches a submission and generates structured feedback for review

---

## Installation

```bash
pip install artemis-cli
```

Or from source:

```bash
git clone https://github.com/wiestju/artemis-cli
cd artemis-cli
pip install -e .
```

Requires Python 3.10+.

---

## Authentication

### University / SSO login (KIT, TUM, …)

Most Artemis instances (including KIT) use SSO and do not accept password login via the API.

1. Log in at your Artemis instance in the browser
2. Open DevTools → **Application** → **Cookies**
3. Copy the value of the `jwt` cookie
4. Run:

```bash
artemis login --server https://artemis.cs.kit.edu --token <jwt>
```

The token is stored securely in your system keyring. Re-run this command when the token expires (usually after a few days).

### Internal accounts (non-SSO instances)

```bash
artemis login --server https://your-artemis.example.com
# prompts for username and password
```

---

## Quickstart

```bash
# See your courses
artemis courses list

# Exercises in a course
artemis courses exercises 42

# Read an exercise
artemis exercises view 123

# --- Tutor workflow ---

# How many submissions are left to grade?
artemis exercises dashboard 123

# Get the next submission to grade (locks it)
artemis exercises next 123

# Grade it interactively
artemis assess interactive <participation_id>

# Or submit a prepared JSON assessment
artemis assess submit <participation_id> --feedbacks feedbacks.json

# Changed your mind? Release the lock
artemis assess cancel <submission_id>

# View the submission content
artemis submissions view <participation_id>

# Check existing result + feedbacks
artemis submissions result <participation_id>

# Complaints
artemis complaints list 123
artemis complaints respond <complaint_id>
```

---

## Command Reference

### Auth

| Command | Description |
| --- | --- |
| `artemis login` | Authenticate and store credentials |
| `artemis logout` | Clear stored credentials |
| `artemis whoami` | Show current server and token status |

**Options for `login`:**

- `--server` / `-s` — Artemis server URL
- `--token` / `-t` — Paste JWT directly (for SSO instances)
- `--username` / `-u` — Username (non-SSO only)
- `--password` / `-p` — Password (non-SSO only)

### Courses

| Command | Description |
| --- | --- |
| `artemis courses list` | List enrolled courses with your role |
| `artemis courses exercises <course_id>` | List exercises for a course |

### Exercises

| Command | Description |
| --- | --- |
| `artemis exercises view <id>` | Show exercise details and problem statement |
| `artemis exercises dashboard <id>` | Assessment progress stats (tutor+) |
| `artemis exercises next <id>` | Lock and display the next unassessed submission |
| `artemis exercises submissions <id>` | List all submissions (instructor only) |

**Options for `exercises next`:**

- `--correction-round 0\|1` — First or second correction round (default: `0`)

### Submissions

| Command | Description |
| --- | --- |
| `artemis submissions view <participation_id>` | Show latest submission content |
| `artemis submissions result <participation_id>` | Show assessed result and all feedbacks |
| `artemis submissions download <participation_id>` | Save file-upload submission to disk |

**Options for `submissions download`:**

- `--output` / `-o` — Output file path (default: `submission_<id>.zip`)

### Assess

| Command | Description |
| --- | --- |
| `artemis assess interactive <participation_id>` | Interactive grading REPL |
| `artemis assess submit <participation_id>` | Submit a pre-built assessment |
| `artemis assess cancel <submission_id>` | Release a locked submission without grading |
| `artemis assess external <exercise_id>` | Submit result for a student without a participation |

**Options for `assess submit`:**

- `--type text\|modeling\|file-upload\|programming` (default: `text`)
- `--feedbacks` / `-f` — JSON array or path to `.json` file
- `--result-id` — Update an existing result
- `--note` — Internal assessor note
- `--draft` — Save without finalising

**Options for `assess external`:**

- `--student` — Student login (e.g. `uXXXX`) *(required)*
- `--score` — Score as a number *(required)*
- `--feedbacks` / `-f` — JSON array or path to `.json` file

### Complaints

| Command | Description |
| --- | --- |
| `artemis complaints list <exercise_id>` | List grade complaints |
| `artemis complaints feedback-list <exercise_id>` | List more-feedback requests |
| `artemis complaints respond <complaint_id>` | Respond to a complaint |
| `artemis complaints unlock <complaint_id>` | Release a locked complaint |

**Options for `complaints respond`:**

- `--text` / `-t` — Response text (prompted if omitted)
- `--accept` / `--reject` — Decision (prompted if omitted)

---

## Feedback JSON format

Used with `assess submit --feedbacks` and `assess external --feedbacks`:

```json
[
  {
    "text": "Good explanation of the concept",
    "detailText": "See section 2",
    "credits": 3.0,
    "type": "MANUAL_UNREFERENCED"
  },
  {
    "text": "Missing error handling",
    "credits": -1.0,
    "type": "MANUAL_UNREFERENCED"
  }
]
```

---

## Tutor workflow

```bash
artemis exercises dashboard <exercise_id>    # check progress
artemis exercises next <exercise_id>         # lock next submission
                                             # → note the participation_id
artemis submissions view <participation_id>  # read the submission
artemis assess interactive <participation_id>  # grade it
```

To undo a lock without grading:

```bash
artemis assess cancel <submission_id>
```

---

## AI grading assistant (Claude Code skill)

The repo ships a ready-to-use [Claude Code](https://claude.ai/code) skill at `.claude/skills/artemis-grade.md`.

**Setup:**

1. Install the AI extras: `pip install 'artemis-cli[ai]'`
2. Add your Anthropic API key to `.env`: `ANTHROPIC_API_KEY=sk-ant-...`
3. Make sure you are authenticated: `artemis whoami`

**Usage inside Claude Code:**

```text
/artemis-grade
```

Claude will ask for a `participation_id` and `exercise_id`, fetch the submission and exercise description, generate structured feedback, let you review and edit it, then submit to Artemis on confirmation.

The skill is purely read-then-submit — it never modifies data without your explicit approval.

---

## Credential storage

- Server URL is stored in `~/.artemis/config.json`
- JWT token is stored in the **system keyring** (macOS Keychain, Windows Credential Manager, Linux Secret Service) if available, otherwise in `~/.artemis/config.json` with permissions `600`

---

## Running the tests

Integration tests run against a live Artemis instance. Copy `.env.example` to `.env` and fill in your credentials:

```bash
pip install -e ".[dev]"
cp .env.example .env
# fill in ARTEMIS_TOKEN (or ARTEMIS_USERNAME + ARTEMIS_PASSWORD)
pytest
```

All IDs (course, exercise) are auto-detected — no manual configuration needed.

---

## Compatibility

Tested against **Artemis 8.x** (KIT instance). The API structure has changed across versions; if you encounter unexpected 404s, your instance may be running an older release.

---

## Contributing

Contributions are very welcome — this project is intentionally open for the community to extend.

**Good first contributions:**

- Support for additional Artemis API endpoints (programming exercises, quiz results, exam management)
- Additional Claude Code skills (e.g. `/artemis-dashboard`, `/artemis-complaints`)
- Better output formatting or export options (CSV, JSON)
- Support for other Artemis instances (configure your university's URL in `.env`)
- Improved test coverage against real Artemis instances

**How to contribute:**

1. Fork the repo and create a branch: `git checkout -b feature/my-feature`
2. Install dev dependencies: `pip install -e ".[dev]"`
3. Make your changes and run the tests: `pytest`
4. Open a pull request — describe what you changed and why

Please open an issue first for larger changes so we can discuss the approach before you invest time writing code.

---

## License

MIT
