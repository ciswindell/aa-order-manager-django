"""Shared utilities for workflow services."""

from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from orders.models import Report


def format_report_description(report: "Report") -> str:
    """
    Format report legal description with date range.

    Date range formatting rules:
    - Both dates: "Legal desc from M/D/YYYY to M/D/YYYY"
    - No dates: "Legal desc"
    - Only start: "Legal desc from M/D/YYYY to present"
    - Only end: "Legal desc from inception to M/D/YYYY"

    Args:
        report: Report object with legal_description, start_date, end_date

    Returns:
        Formatted string with legal description and date range
    """
    legal_desc = report.legal_description or "[No description]"

    # Both dates present
    if report.start_date and report.end_date:
        start_str = _format_date(report.start_date)
        end_str = _format_date(report.end_date)
        return f"{legal_desc} from {start_str} to {end_str}"

    # Only start date
    if report.start_date and not report.end_date:
        start_str = _format_date(report.start_date)
        return f"{legal_desc} from {start_str} to present"

    # Only end date
    if not report.start_date and report.end_date:
        end_str = _format_date(report.end_date)
        return f"{legal_desc} from inception to {end_str}"

    # No dates
    return legal_desc


def _format_date(d: date) -> str:
    """
    Format date as M/D/YYYY (no zero-padding).

    Args:
        d: Date object

    Returns:
        Formatted string like "1/1/1979" or "12/25/2024"
    """
    return f"{d.month}/{d.day}/{d.year}"

