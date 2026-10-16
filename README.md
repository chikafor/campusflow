# CampusFlow

CampusFlow is a Python command-line support ticket tracker built for the AI-Native Engineering Sprint. It uses Python's standard library and JSON file storage.

## Features

- Create, view, assign, and search support tickets.
- Filter tickets by fields such as category and status.
- Calculate ticket priority from urgency and affected-user count.
- Enforce ticket workflow rules and prevent invalid state changes.
- Add notes to tickets.
- Display the open-ticket queue in priority order.
- Generate reports, including ticket counts and resolution percentage.
- Save and reload ticket data using JSON.
- Run the Engineering Understanding Check to practise explaining engineering decisions.

## Requirements and constraints

- Python 3.
- Python standard library only.
- `unittest` for automated tests.
- JSON for persistent storage.
- No database, web framework, or external application API.

## Team

- Engineer A: Bront888 — ticket foundation and JSON persistence.
- Engineer B: chikafor — ticket search and filters, reporting, and Engineering Understanding Check.

## Design decisions

- Queue policy: open tickets only.
- Resolved-ticket policy: mutations are blocked until an explicit reopen, where permitted by the workflow.
- Storage uses JSON.
- Invalid operations should be handled without unintended changes to ticket data.

See [docs/design-decisions.md](docs/design-decisions.md) for the shared design decisions and acceptance rules.

## Run the application

```bash
python3 main.py
