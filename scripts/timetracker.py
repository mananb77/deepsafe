#!/usr/bin/env python3
"""
DeepSafe Development Time Tracker

A CLI tool for tracking development time on the DeepSafe project.
Supports clock in/out, breaks, task tagging, and reporting.

Usage:
    python timetracker.py clock-in [--task TASK] [--notes NOTES]
    python timetracker.py clock-out [--notes NOTES]
    python timetracker.py break start
    python timetracker.py break end
    python timetracker.py status
    python timetracker.py log [--days DAYS]
    python timetracker.py report [--week|--month|--all]
    python timetracker.py export [--format csv|json]
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum


# Configuration
DATA_DIR = Path(__file__).parent.parent / ".timetracker"
DATA_FILE = DATA_DIR / "sessions.json"
CONFIG_FILE = DATA_DIR / "config.json"


class SessionStatus(str, Enum):
    ACTIVE = "active"
    ON_BREAK = "on_break"
    COMPLETED = "completed"


@dataclass
class Break:
    """Represents a break during a work session."""
    start: str
    end: Optional[str] = None
    duration_minutes: Optional[float] = None


@dataclass
class Session:
    """Represents a work session."""
    id: str
    clock_in: str
    clock_out: Optional[str] = None
    task: Optional[str] = None
    notes: Optional[str] = None
    status: str = SessionStatus.ACTIVE.value
    breaks: List[Dict] = None
    total_break_minutes: float = 0
    work_minutes: Optional[float] = None

    def __post_init__(self):
        if self.breaks is None:
            self.breaks = []


class TimeTracker:
    """Main time tracking class."""

    def __init__(self):
        self._ensure_data_dir()
        self.sessions: List[Dict] = self._load_sessions()
        self.config = self._load_config()

    def _ensure_data_dir(self):
        """Create data directory if it doesn't exist."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    def _load_sessions(self) -> List[Dict]:
        """Load sessions from file."""
        if DATA_FILE.exists():
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        return []

    def _save_sessions(self):
        """Save sessions to file."""
        with open(DATA_FILE, "w") as f:
            json.dump(self.sessions, f, indent=2, default=str)

    def _load_config(self) -> Dict:
        """Load configuration."""
        default_config = {
            "project_name": "DeepSafe",
            "default_task": "development",
            "work_day_hours": 8,
            "timezone": "local"
        }
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r") as f:
                return {**default_config, **json.load(f)}
        return default_config

    def _generate_id(self) -> str:
        """Generate unique session ID."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _get_active_session(self) -> Optional[Dict]:
        """Get currently active session."""
        for session in reversed(self.sessions):
            if session["status"] in [SessionStatus.ACTIVE.value, SessionStatus.ON_BREAK.value]:
                return session
        return None

    def _format_duration(self, minutes: float) -> str:
        """Format duration in hours and minutes."""
        hours = int(minutes // 60)
        mins = int(minutes % 60)
        if hours > 0:
            return f"{hours}h {mins}m"
        return f"{mins}m"

    def _parse_datetime(self, dt_str: str) -> datetime:
        """Parse datetime string."""
        return datetime.fromisoformat(dt_str)

    def clock_in(self, task: Optional[str] = None, notes: Optional[str] = None) -> Dict:
        """Start a new work session."""
        # Check for existing active session
        active = self._get_active_session()
        if active:
            print(f"Error: Already clocked in since {active['clock_in']}")
            print(f"Task: {active.get('task', 'N/A')}")
            print("Use 'clock-out' first or 'status' to check current session.")
            sys.exit(1)

        session = Session(
            id=self._generate_id(),
            clock_in=datetime.now().isoformat(),
            task=task or self.config.get("default_task"),
            notes=notes,
            status=SessionStatus.ACTIVE.value,
        )

        self.sessions.append(asdict(session))
        self._save_sessions()

        print("=" * 50)
        print(f"  CLOCKED IN - {self.config['project_name']}")
        print("=" * 50)
        print(f"  Time:  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Task:  {session.task}")
        if notes:
            print(f"  Notes: {notes}")
        print("=" * 50)

        return asdict(session)

    def clock_out(self, notes: Optional[str] = None) -> Dict:
        """End the current work session."""
        active = self._get_active_session()
        if not active:
            print("Error: Not currently clocked in.")
            print("Use 'clock-in' to start a session.")
            sys.exit(1)

        # End any active break
        if active["status"] == SessionStatus.ON_BREAK.value:
            self._end_break(active)

        clock_out_time = datetime.now()
        clock_in_time = self._parse_datetime(active["clock_in"])

        # Calculate work time
        total_minutes = (clock_out_time - clock_in_time).total_seconds() / 60
        work_minutes = total_minutes - active.get("total_break_minutes", 0)

        # Update session
        active["clock_out"] = clock_out_time.isoformat()
        active["status"] = SessionStatus.COMPLETED.value
        active["work_minutes"] = round(work_minutes, 2)

        if notes:
            existing_notes = active.get("notes", "")
            active["notes"] = f"{existing_notes}\n[Clock-out] {notes}".strip()

        self._save_sessions()

        print("=" * 50)
        print(f"  CLOCKED OUT - {self.config['project_name']}")
        print("=" * 50)
        print(f"  Clock In:    {clock_in_time.strftime('%H:%M:%S')}")
        print(f"  Clock Out:   {clock_out_time.strftime('%H:%M:%S')}")
        print(f"  Total Time:  {self._format_duration(total_minutes)}")
        print(f"  Break Time:  {self._format_duration(active.get('total_break_minutes', 0))}")
        print(f"  Work Time:   {self._format_duration(work_minutes)}")
        print(f"  Task:        {active.get('task', 'N/A')}")
        print("=" * 50)

        return active

    def _end_break(self, session: Dict):
        """End an active break."""
        if session["breaks"]:
            current_break = session["breaks"][-1]
            if current_break.get("end") is None:
                current_break["end"] = datetime.now().isoformat()
                start = self._parse_datetime(current_break["start"])
                end = self._parse_datetime(current_break["end"])
                duration = (end - start).total_seconds() / 60
                current_break["duration_minutes"] = round(duration, 2)
                session["total_break_minutes"] = sum(
                    b.get("duration_minutes", 0) for b in session["breaks"]
                )

    def start_break(self) -> Dict:
        """Start a break."""
        active = self._get_active_session()
        if not active:
            print("Error: Not currently clocked in.")
            sys.exit(1)

        if active["status"] == SessionStatus.ON_BREAK.value:
            print("Error: Already on break.")
            sys.exit(1)

        break_entry = Break(start=datetime.now().isoformat())
        active["breaks"].append(asdict(break_entry))
        active["status"] = SessionStatus.ON_BREAK.value
        self._save_sessions()

        print("=" * 50)
        print("  BREAK STARTED")
        print("=" * 50)
        print(f"  Time: {datetime.now().strftime('%H:%M:%S')}")
        print("  Use 'break end' to resume work.")
        print("=" * 50)

        return active

    def end_break(self) -> Dict:
        """End a break."""
        active = self._get_active_session()
        if not active:
            print("Error: Not currently clocked in.")
            sys.exit(1)

        if active["status"] != SessionStatus.ON_BREAK.value:
            print("Error: Not currently on break.")
            sys.exit(1)

        self._end_break(active)
        active["status"] = SessionStatus.ACTIVE.value
        self._save_sessions()

        last_break = active["breaks"][-1]

        print("=" * 50)
        print("  BREAK ENDED")
        print("=" * 50)
        print(f"  Break Duration: {self._format_duration(last_break['duration_minutes'])}")
        print(f"  Total Breaks:   {self._format_duration(active['total_break_minutes'])}")
        print("=" * 50)

        return active

    def status(self):
        """Show current session status."""
        active = self._get_active_session()

        print("=" * 50)
        print(f"  STATUS - {self.config['project_name']}")
        print("=" * 50)

        if not active:
            print("  Status: NOT CLOCKED IN")
            print()
            # Show last session
            completed = [s for s in self.sessions if s["status"] == SessionStatus.COMPLETED.value]
            if completed:
                last = completed[-1]
                print("  Last Session:")
                print(f"    Date: {self._parse_datetime(last['clock_in']).strftime('%Y-%m-%d')}")
                print(f"    Work: {self._format_duration(last.get('work_minutes', 0))}")
        else:
            status_emoji = "🔴" if active["status"] == SessionStatus.ON_BREAK.value else "🟢"
            print(f"  Status: {status_emoji} {active['status'].upper()}")
            print()

            clock_in = self._parse_datetime(active["clock_in"])
            elapsed = (datetime.now() - clock_in).total_seconds() / 60
            work_time = elapsed - active.get("total_break_minutes", 0)

            print(f"  Clock In:     {clock_in.strftime('%H:%M:%S')}")
            print(f"  Task:         {active.get('task', 'N/A')}")
            print(f"  Elapsed:      {self._format_duration(elapsed)}")
            print(f"  Break Time:   {self._format_duration(active.get('total_break_minutes', 0))}")
            print(f"  Work Time:    {self._format_duration(work_time)}")

            if active["status"] == SessionStatus.ON_BREAK.value:
                current_break = active["breaks"][-1]
                break_start = self._parse_datetime(current_break["start"])
                break_elapsed = (datetime.now() - break_start).total_seconds() / 60
                print(f"  Current Break: {self._format_duration(break_elapsed)}")

        print("=" * 50)

    def log(self, days: int = 7):
        """Show session log for recent days."""
        cutoff = datetime.now() - timedelta(days=days)

        print("=" * 60)
        print(f"  SESSION LOG - Last {days} days")
        print("=" * 60)

        daily_totals: Dict[str, float] = {}

        for session in self.sessions:
            clock_in = self._parse_datetime(session["clock_in"])
            if clock_in < cutoff:
                continue

            date_key = clock_in.strftime("%Y-%m-%d")
            work_minutes = session.get("work_minutes", 0)

            if session["status"] != SessionStatus.COMPLETED.value:
                # Calculate for active session
                elapsed = (datetime.now() - clock_in).total_seconds() / 60
                work_minutes = elapsed - session.get("total_break_minutes", 0)

            daily_totals[date_key] = daily_totals.get(date_key, 0) + work_minutes

            status_icon = "✓" if session["status"] == SessionStatus.COMPLETED.value else "⏳"

            print(f"\n  {status_icon} {date_key}")
            print(f"    Task: {session.get('task', 'N/A')}")
            print(f"    In:   {clock_in.strftime('%H:%M')}", end="")

            if session.get("clock_out"):
                clock_out = self._parse_datetime(session["clock_out"])
                print(f"  Out: {clock_out.strftime('%H:%M')}", end="")

            print(f"  Work: {self._format_duration(work_minutes)}")

        print("\n" + "-" * 60)
        print("  Daily Totals:")

        total_work = 0
        for date, minutes in sorted(daily_totals.items()):
            total_work += minutes
            target_hours = self.config.get("work_day_hours", 8)
            target_minutes = target_hours * 60
            percentage = (minutes / target_minutes) * 100
            bar_length = int(percentage / 5)
            bar = "█" * min(bar_length, 20) + "░" * (20 - min(bar_length, 20))
            print(f"    {date}: [{bar}] {self._format_duration(minutes)} ({percentage:.0f}%)")

        print("-" * 60)
        print(f"  Total: {self._format_duration(total_work)}")
        print("=" * 60)

    def report(self, period: str = "week"):
        """Generate a summary report."""
        now = datetime.now()

        if period == "week":
            start = now - timedelta(days=now.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            title = f"Weekly Report ({start.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')})"
        elif period == "month":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            title = f"Monthly Report ({now.strftime('%B %Y')})"
        else:  # all
            start = datetime.min
            title = "All Time Report"

        sessions_in_period = [
            s for s in self.sessions
            if self._parse_datetime(s["clock_in"]) >= start
        ]

        total_work = 0
        total_breaks = 0
        tasks: Dict[str, float] = {}
        daily_work: Dict[str, float] = {}

        for session in sessions_in_period:
            work = session.get("work_minutes", 0)
            if session["status"] != SessionStatus.COMPLETED.value:
                clock_in = self._parse_datetime(session["clock_in"])
                elapsed = (datetime.now() - clock_in).total_seconds() / 60
                work = elapsed - session.get("total_break_minutes", 0)

            total_work += work
            total_breaks += session.get("total_break_minutes", 0)

            task = session.get("task", "uncategorized")
            tasks[task] = tasks.get(task, 0) + work

            date = self._parse_datetime(session["clock_in"]).strftime("%Y-%m-%d")
            daily_work[date] = daily_work.get(date, 0) + work

        print("=" * 60)
        print(f"  {title}")
        print("=" * 60)

        print(f"\n  Summary:")
        print(f"    Sessions:     {len(sessions_in_period)}")
        print(f"    Total Work:   {self._format_duration(total_work)}")
        print(f"    Total Breaks: {self._format_duration(total_breaks)}")
        print(f"    Days Worked:  {len(daily_work)}")

        if daily_work:
            avg_daily = total_work / len(daily_work)
            print(f"    Avg per Day:  {self._format_duration(avg_daily)}")

        print(f"\n  By Task:")
        for task, minutes in sorted(tasks.items(), key=lambda x: -x[1]):
            percentage = (minutes / total_work * 100) if total_work > 0 else 0
            print(f"    {task}: {self._format_duration(minutes)} ({percentage:.1f}%)")

        print("=" * 60)

    def export(self, format: str = "json") -> str:
        """Export sessions to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format == "csv":
            filename = DATA_DIR / f"export_{timestamp}.csv"
            import csv
            with open(filename, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "ID", "Clock In", "Clock Out", "Task", "Status",
                    "Work Minutes", "Break Minutes", "Notes"
                ])
                for session in self.sessions:
                    writer.writerow([
                        session.get("id", ""),
                        session.get("clock_in", ""),
                        session.get("clock_out", ""),
                        session.get("task", ""),
                        session.get("status", ""),
                        session.get("work_minutes", ""),
                        session.get("total_break_minutes", ""),
                        session.get("notes", ""),
                    ])
        else:  # json
            filename = DATA_DIR / f"export_{timestamp}.json"
            with open(filename, "w") as f:
                json.dump(self.sessions, f, indent=2)

        print(f"Exported to: {filename}")
        return str(filename)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="DeepSafe Development Time Tracker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s clock-in --task "Phase 2: API Service"
  %(prog)s clock-in --task "Bug fix" --notes "Fixing auth issue"
  %(prog)s break start
  %(prog)s break end
  %(prog)s clock-out --notes "Completed auth endpoints"
  %(prog)s status
  %(prog)s log --days 14
  %(prog)s report --week
  %(prog)s export --format csv
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Clock in
    clock_in_parser = subparsers.add_parser("clock-in", help="Start a work session")
    clock_in_parser.add_argument("--task", "-t", help="Task or phase name")
    clock_in_parser.add_argument("--notes", "-n", help="Session notes")

    # Clock out
    clock_out_parser = subparsers.add_parser("clock-out", help="End current session")
    clock_out_parser.add_argument("--notes", "-n", help="Closing notes")

    # Break
    break_parser = subparsers.add_parser("break", help="Manage breaks")
    break_parser.add_argument("action", choices=["start", "end"], help="Break action")

    # Status
    subparsers.add_parser("status", help="Show current status")

    # Log
    log_parser = subparsers.add_parser("log", help="Show session log")
    log_parser.add_argument("--days", "-d", type=int, default=7, help="Days to show")

    # Report
    report_parser = subparsers.add_parser("report", help="Generate summary report")
    report_group = report_parser.add_mutually_exclusive_group()
    report_group.add_argument("--week", "-w", action="store_true", help="Weekly report")
    report_group.add_argument("--month", "-m", action="store_true", help="Monthly report")
    report_group.add_argument("--all", "-a", action="store_true", help="All time report")

    # Export
    export_parser = subparsers.add_parser("export", help="Export sessions")
    export_parser.add_argument(
        "--format", "-f",
        choices=["csv", "json"],
        default="json",
        help="Export format"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    tracker = TimeTracker()

    if args.command == "clock-in":
        tracker.clock_in(task=args.task, notes=args.notes)
    elif args.command == "clock-out":
        tracker.clock_out(notes=args.notes)
    elif args.command == "break":
        if args.action == "start":
            tracker.start_break()
        else:
            tracker.end_break()
    elif args.command == "status":
        tracker.status()
    elif args.command == "log":
        tracker.log(days=args.days)
    elif args.command == "report":
        if args.month:
            tracker.report(period="month")
        elif args.all:
            tracker.report(period="all")
        else:
            tracker.report(period="week")
    elif args.command == "export":
        tracker.export(format=args.format)


if __name__ == "__main__":
    main()
