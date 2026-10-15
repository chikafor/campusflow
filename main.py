"""Interactive command-line interface for CampusFlow.

Business rules live in campusflow modules; this file handles user interaction,
display, persistence orchestration, and friendly error messages.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

from campusflow.reports import generate_report
from campusflow.storage import StorageError, load_tickets, save_tickets
from campusflow.tickets import create_ticket, find_ticket, search_tickets
from campusflow.workflow import (
    assign_ticket,
    change_status,
    get_open_queue,
    reopen_ticket,
)

Ticket = dict[str, Any]
DEFAULT_DATA_FILE = Path("data/tickets.json")


def parse_args() -> argparse.Namespace:
    """Parse optional CLI configuration."""
    parser = argparse.ArgumentParser(description="CampusFlow ticket tracker")
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATA_FILE,
        help=f"path to the JSON ticket file (default: {DEFAULT_DATA_FILE})",
    )
    return parser.parse_args()


def prompt_positive_integer(prompt: str) -> int:
    """Read a positive integer, rejecting decimals, zero, and negatives."""
    raw_value = input(prompt).strip()
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ValueError("Enter a whole number, such as 1 or 12.") from exc

    if value <= 0:
        raise ValueError("Enter a number greater than zero.")
    return value


def print_ticket(ticket: Ticket) -> None:
    """Display a ticket in a consistent, readable format."""
    print("-" * 44)
    print(f"ID:             {ticket['id']}")
    print(f"Title:          {ticket['title']}")
    print(f"Category:       {ticket['category']}")
    print(f"Urgency:        {ticket['urgency']}")
    print(f"Affected users: {ticket['affected_users']}")
    print(f"Priority:       {ticket['priority'].upper()}")
    print(f"Status:         {ticket['status'].replace('_', ' ').title()}")
    print(f"Assigned to:    {ticket['assigned_to'] or 'Unassigned'}")
    print("-" * 44)


def print_ticket_list(tickets: list[Ticket]) -> None:
    """Display tickets, or an explicit empty-state message."""
    if not tickets:
        print("No tickets found.")
        return

    for ticket in sorted(tickets, key=lambda item: item["id"]):
        print_ticket(ticket)


def run_mutation(
    tickets: list[Ticket],
    data_path: Path,
    operation: Callable[[], Any],
) -> Any | None:
    """Run a mutation and persist it, rolling back memory if either step fails."""
    before = deepcopy(tickets)

    try:
        result = operation()
        save_tickets(data_path, tickets)
    except (ValueError, KeyError, StorageError) as exc:
        tickets[:] = before
        print(f"Error: {exc}")
        return None

    print(f"Saved to {data_path}.")
    return result


def create_ticket_menu(tickets: list[Ticket], data_path: Path) -> None:
    print("\nCreate a ticket")
    title = input("Title: ").strip()
    category = input("Category (Network/Hardware/Software/Other): ").strip()
    urgency = input("Urgency (low/medium/high): ").strip()

    try:
        affected_users = prompt_positive_integer("Number of affected users: ")
    except ValueError as exc:
        print(f"Error: {exc}")
        return

    ticket = run_mutation(
        tickets,
        data_path,
        lambda: create_ticket(
            tickets, title, category, urgency, affected_users
        ),
    )
    if ticket is not None:
        print("Ticket created successfully.")
        print_ticket(ticket)


def view_ticket_menu(tickets: list[Ticket]) -> None:
    try:
        ticket_id = prompt_positive_integer("Ticket ID: ")
        print_ticket(find_ticket(tickets, ticket_id))
    except (ValueError, KeyError) as exc:
        print(f"Error: {exc}")

def search_tickets_menu(tickets: list[Ticket]) -> None:
    print("\nSearch tickets")
    query = input("Search word or phrase (press Enter to skip): ").strip()
    status = input("Status filter (open/in_progress/resolved, Enter to skip): ").strip()
    priority = input("Priority filter (low/medium/high/critical, Enter to skip): ").strip()
    category = input("Category filter (Network/Hardware/Software/Other, Enter to skip): ").strip()

    results = search_tickets(
        tickets,
        query=query,
        status=status or None,
        priority=priority or None,
        category=category or None,
    )

    print(f"\nFound {len(results)} matching ticket(s).")
    print_ticket_list(results)

def assign_ticket_menu(tickets: list[Ticket], data_path: Path) -> None:
    try:
        ticket_id = prompt_positive_integer("Ticket ID to assign: ")
    except ValueError as exc:
        print(f"Error: {exc}")
        return

    staff_name = input("Staff member name: ").strip()
    ticket = run_mutation(
        tickets,
        data_path,
        lambda: assign_ticket(tickets, ticket_id, staff_name),
    )
    if ticket is not None:
        print(f"Ticket #{ticket_id} assigned to {ticket['assigned_to']}.")


def change_status_menu(tickets: list[Ticket], data_path: Path) -> None:
    try:
        ticket_id = prompt_positive_integer("Ticket ID: ")
    except ValueError as exc:
        print(f"Error: {exc}")
        return

    new_status = input(
        "New status (in_progress/resolved): "
    ).strip()
    ticket = run_mutation(
        tickets,
        data_path,
        lambda: change_status(tickets, ticket_id, new_status),
    )
    if ticket is not None:
        print(f"Ticket #{ticket_id} is now {ticket['status']}.")


def reopen_ticket_menu(tickets: list[Ticket], data_path: Path) -> None:
    try:
        ticket_id = prompt_positive_integer("Ticket ID to reopen: ")
    except ValueError as exc:
        print(f"Error: {exc}")
        return

    ticket = run_mutation(
        tickets,
        data_path,
        lambda: reopen_ticket(tickets, ticket_id),
    )
    if ticket is not None:
        print(f"Ticket #{ticket_id} has been reopened.")


def show_open_queue(tickets: list[Ticket]) -> None:
    queue = get_open_queue(tickets)
    if not queue:
        print("The open queue is empty.")
        return

    print("\nOpen queue (highest priority first)")
    for ticket in queue:
        print(
            f"#{ticket['id']} [{ticket['priority'].upper()}] "
            f"{ticket['title']} — {ticket['category']}"
        )


def show_report(tickets: list[Ticket]) -> None:
    report = generate_report(tickets)
    print("\nCampusFlow report")
    print(f"Total tickets: {report['total']}")

    print("\nBy status:")
    for status, count in report["by_status"].items():
        print(f"  {status.replace('_', ' ').title():<14} {count}")

    print("\nBy priority:")
    for priority, count in report["by_priority"].items():
        print(f"  {priority.title():<14} {count}")


def print_menu() -> None:
    print(
        "\n=== CampusFlow ===\n"
        "1. Create ticket\n"
        "2. List all tickets\n"
        "3. View ticket by ID\n"
        "4. Assign ticket\n"
        "5. Change ticket status\n"
        "6. Reopen resolved ticket\n"
        "7. Show open queue\n"
        "8. Generate report\n"
        "9. search tickets\n"
        "10. Exit"
    )


def main() -> int:
    args = parse_args()

    try:
        tickets = load_tickets(args.data)
    except StorageError as exc:
        # Do not continue with an empty list: doing so could overwrite bad data.
        print(f"Startup error: {exc}")
        print("Fix or restore the data file, then run CampusFlow again.")
        return 1

    print(f"Loaded {len(tickets)} ticket(s) from {args.data}.")

    actions: dict[str, Callable[[], None]] = {
        "1": lambda: create_ticket_menu(tickets, args.data),
        "2": lambda: print_ticket_list(tickets),
        "3": lambda: view_ticket_menu(tickets),
        "4": lambda: assign_ticket_menu(tickets, args.data),
        "5": lambda: change_status_menu(tickets, args.data),
        "6": lambda: reopen_ticket_menu(tickets, args.data),
        "7": lambda: show_open_queue(tickets),
        "8": lambda: show_report(tickets),
        "9": lambda: search_tickets_menu(tickets),
    }

    while True:
        print_menu()
        choice = input("Choose an option (1-10): ").strip()

        if choice == "10":
            print("CampusFlow closed.")
            return 0

        action = actions.get(choice)
        if action is None:
            print("Invalid choice. Enter a number from 1 to 10.")
            continue

        try:
            action()
        except (ValueError, KeyError, StorageError) as exc:
            # Covers malformed business data surfaced by read-only operations.
            print(f"Error: {exc}")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyboardInterrupt, EOFError):
        print("\nCampusFlow closed.")
        raise SystemExit(0)