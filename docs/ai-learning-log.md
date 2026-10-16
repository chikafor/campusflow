# AI Learning Log

## Entry 1 — Understanding ticket search and filters

- **Engineer:** chikafor (Engineer B)
- **Date:** 2026-10-16
- **Question discussed:** How do ticket search and filters work when a ticket must match more than one condition?
- **AI response or idea tested:** I learned that AND filtering requires a ticket to satisfy every selected condition.
- **Experiment or application:** I practised identifying whether tickets matched both the Network category and Open status.
- **Independent verification:** I located the search tests using grep and ran `python3 -m unittest discover -s tests -p 'test_tickets.py' -v`.
- **Verification result:** All 21 tests passed, including tests for case-insensitive search, category filtering, AND logic, and searches with no matches.
- **Outcome in my own words:** I learned that AND filtering means all selected conditions must match. I also learned how to locate the relevant tests and run the correct test file.
- **Correction or rejection:** My first test command targeted `tests.test_search`, but that module did not exist. I checked the test directory, found the search tests in `test_tickets.py`, and ran the correct command successfully.