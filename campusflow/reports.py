"""Aggregate ticket counts for the CampusFlow CLI."""

from __future__ import annotations

from typing import Any, Iterable

Ticket = dict[str, Any]

_STATUSES = ("open", "in_progress", "resolved")
_PRIORITIES = ("critical", "high", "medium", "low")


def generate_report(tickets: Iterable[Ticket]) -> dict[str, Any]:
    """Return total, status counts, and priority counts.

    Every supported status and priority is included, even when its count is
    zero. The input iterable is read but never modified.
    """
    status_counts = {status: 0 for status in _STATUSES}
    priority_counts = {priority: 0 for priority in _PRIORITIES}
    total = 0

    for ticket in tickets:
        total += 1
        status = ticket.get("status")
        priority = ticket.get("priority")

        if status not in status_counts:
            raise ValueError(f"Unknown ticket status: {status!r}.")
        if priority not in priority_counts:
            raise ValueError(f"Unknown ticket priority: {priority!r}.")

        status_counts[status] += 1
        priority_counts[priority] += 1

    resolved = status_counts["resolved"]
    resolution_percentage = (resolved / total * 100) if total else 0.0

    return {
        "total": total,
        "by_status": status_counts,
        "by_priority": priority_counts,
        "resolution_percentage": resolution_percentage,
    }
