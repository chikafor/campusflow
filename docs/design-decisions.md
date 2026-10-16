# CampusFlow Design Decisions

## 1. Purpose and scope

CampusFlow is a standard-library Python command-line ticket tracker for the AI-Native Engineering Sprint. It supports ticket creation, viewing, assignment, workflow transitions, an open-ticket queue, reports, and JSON persistence.

Constraints:
- Python standard library only for the application and tests.
- Use `unittest` for automated tests and `json` for persistence.
- No database, web API, or third-party application framework.
- Keep input/output in the CLI; business logic must be testable without interactive prompts.

## 2. Architecture and module responsibilities

- `main.py`: menu loop, input/output, friendly error messages, and orchestration.
- `campusflow/tickets.py`: ticket validation, creation, lookup, ID allocation, and priority calculation.
- `campusflow/workflow.py`: assignment, status transitions, reopening, and open queue.
- `campusflow/storage.py`: JSON loading/saving and validation of persisted records.
- `campusflow/reports.py`: total, status, and priority counts.
- `tests/`: automated tests independent of interactive menu input.
- `docs/`: design decisions and genuine AI learning log.

Modules must not prompt users for input. The CLI calls business functions and translates expected exceptions into readable messages.

## 3. Ticket data model

Each ticket is a dictionary with these fields:

| Field | Type | Rule |
|---|---|---|
| `id` | integer | Positive, unique, stable across reloads |
| `title` | string | Required; whitespace-only titles rejected |
| `category` | string | `Network`, `Hardware`, `Software`, or `Other` |
| `urgency` | string | `low`, `medium`, or `high` |
| `affected_users` | integer | Positive whole number |
| `priority` | string | Calculated, not user-supplied |
| `status` | string | `open`, `in_progress`, or `resolved` |
| `assigned_to` | string or null | `None` until assigned |

New tickets start with status `open` and `assigned_to = None`. Trim surrounding whitespace and normalize category and urgency case. Invalid categories and urgency values are rejected. Reject zero, negative, decimal, and non-numeric affected-user values.

## 4. Priority algorithm

Evaluate rules in this exact order; the first matching rule wins:

1. High urgency AND at least 10 affected users -> `critical`.
2. High urgency OR at least 10 affected users -> `high`.
3. Medium urgency OR at least 3 affected users -> `medium`.
4. Otherwise -> `low`.

Boundary tests must cover 2/3 users and 9/10 users, and overlapping conditions.

## 5. Workflow and mutation policy

Permitted forward transitions:
- `open -> in_progress`
- `in_progress -> resolved`

An unassigned ticket cannot enter `in_progress`. A resolved ticket cannot be changed or reassigned until the explicit reopen operation sets its status to `open`. Reopening is not an ordinary forward transition and must not be implemented as a generic status change.

Rejected operations must not leave partially modified ticket data.

## 6. Queue and reporting semantics

Queue policy is **open-only**: include tickets whose status is exactly `open`; exclude `in_progress` and `resolved`.

Sort queue results by priority in this order: `critical`, `high`, `medium`, `low`. Within a priority, sort by ascending numeric ticket ID. Return a new sorted list without reordering the caller's collection.

Reports include the total number of tickets, counts by every supported status, and counts by every supported priority. Categories with zero tickets must still appear with count zero. An empty collection must return a valid all-zero report.

## 7. Persistence and error handling

Persist tickets as JSON using the standard library.
- A missing file means a fresh start and returns an empty list.
- Malformed JSON or invalid persisted records must raise a clear storage error; never silently discard or overwrite malformed data.
- Round trips preserve every ticket field and ID.
- ID allocation after reload must avoid collisions.
- Save after each successful mutation. Do not save a rejected operation as a successful change.

### Startup loading policy

CampusFlow loads ticket data once during application startup. If loading fails because the stored data is malformed or invalid, the application reports a startup error and exits with a nonzero status. It does not continue with an empty ticket collection, preventing normal application operations from accidentally overwriting the invalid data.

Runtime reloads are not currently supported. If runtime reload functionality is introduced later, its error-handling and data-preservation behavior must be tested separately.

Expected exceptions:
- `ValueError`: invalid business input, invalid transition, or invalid assignment.
- `KeyError`: requested ticket ID does not exist.
- `StorageError` (a dedicated storage exception): malformed/unusable persisted data or storage failures that the CLI should report clearly.

## 8. Shared function contracts

### `campusflow/tickets.py`
- `create_ticket(tickets, title, category, urgency, affected_users) -> dict`: validate, allocate a unique ID, calculate priority, initialize status/assignment, append and return the new ticket. Invalid inputs raise `ValueError`.
- `find_ticket(tickets, ticket_id) -> dict`: return the ticket or raise `KeyError`.
- `calculate_priority(urgency, affected_users) -> str`: apply the ordered priority rules above.
- `get_next_ticket_id(tickets) -> int`: return the next available positive ID, including after a reload.

### `campusflow/workflow.py`
- `assign_ticket(tickets, ticket_id, staff_name) -> dict`: require an existing ticket and a nonblank staff name; return the updated ticket. Raise `KeyError` for an unknown ID and `ValueError` for invalid assignment or a resolved ticket.
- `change_status(tickets, ticket_id, new_status) -> dict`: enforce allowed transitions and the assignment prerequisite. Raise `KeyError` for an unknown ID and `ValueError` for invalid transitions or mutation of a resolved ticket.
- `reopen_ticket(tickets, ticket_id) -> dict`: explicitly change a resolved ticket to `open`; raise `KeyError` for an unknown ID and `ValueError` if the ticket is not resolved.
- `get_open_queue(tickets) -> list[dict]`: return a newly sorted list of open tickets only.

### `campusflow/reports.py`
- `generate_report(tickets) -> dict`: return total count plus status and priority count mappings; include zero-valued keys.

### `campusflow/storage.py`
- `load_tickets(path) -> list[dict]`: return an empty list when the file is absent; validate loaded records; raise `StorageError` for malformed JSON or unusable persisted data.
- `save_tickets(path, tickets) -> None`: write valid JSON and surface failures clearly.

Function names, arguments, return shapes, and error behavior are shared contracts. Any change requires agreement by both engineers and an update to this document before the other branch relies on it.

## 9. Team ownership and integration

- Engineer A: Bront888 — ticket creation/validation/priority and JSON persistence.
- Engineer B: chikafor — assignment, workflow, queue, and reports.
- Both engineers: agree on contracts, contribute tests, integrate CLI, review the partner's PR, and verify the final application.
- Feature branches use `feat/<issue-number>-<short-description>`.
- Each engineer authors a PR and reviews the partner's PR. Each PR must receive substantive review observations; authors address feedback and may not approve their own PR.
- Run the complete suite on integrated `main` before the demo.

## 10. Testing and acceptance

Run:

```bash
python -m unittest discover -s tests -v
```

Test successful behavior and rejection cases: input normalization, invalid values, priority boundaries, unknown IDs, blank staff names, unassigned transitions, invalid transitions, resolved-ticket immutability, reopen, queue filtering/order, empty reports, missing files, JSON round trips, malformed data, and ID continuity. At least eight meaningful tests are required; broader boundary coverage is expected.

## 11. AI learning and verification

Each engineer records at least three genuine AI learning interactions in `docs/ai-learning-log.md`. Each entry records the real prompt/question, what was tried or learned, how the result was independently verified, and the outcome in the engineer's own words. At least one entry must document a verified correction or rejection of an AI suggestion. Do not fabricate prompts, experiments, or verification evidence.
