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
## Entry 2 — Understanding resolution percentage

- **Engineer:** chikafor (Engineer B)
- **Date:** 2026-10-15
- **Question discussed (summary, not a verbatim quote):** How is the ticket resolution percentage calculated, including when there are no tickets?
- **AI response or idea tested:** We discussed calculating the percentage of tickets resolved out of the total number of tickets, and returning 0% when the total is zero.
- **Experiment or application:** I worked through examples involving resolved and unresolved tickets to understand the calculation.
- **Independent verification:** I ran `python3 -m unittest discover -s tests -p 'test_reports.py' -v`.
- **Verification result:** All 5 reporting tests passed, including `test_resolution_percentage`.
- **Outcome in my own words:** I learned that the resolution percentage represents the share of all tickets that have been resolved. I also learned that an empty ticket collection should produce 0% rather than a division error.

## Entry 3 — Correcting a test-file issue

- **Engineer:** chikafor (Engineer B)
- **Date:** 2026-10-16
- **Problem discussed (summary, not a verbatim quote):** Stray text was found in `tests/test_tickets.py`.
- **AI response or idea tested:** We identified that the stray text needed to be removed, then the tests needed to be run to check the correction.
- **Experiment or application:** The stray text was removed from the test file.
- **Independent verification:** The project test suite was run after the correction.
- **Verification result:** The full suite passed with 62 tests, and the correction was recorded in commit `d6675a6` (`Remove stray text from ticket tests`).
- **Outcome in my own words:** I learned that accidental text in a test file can cause problems, and that running tests after a correction helps verify that the project still works.