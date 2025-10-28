"""Command-line task manager application.

This module implements a lightweight task manager that stores tasks in a
SQLite database and exposes a user-friendly CLI for managing personal tasks.
"""
from __future__ import annotations

import argparse
import sqlite3
from dataclasses import dataclass
from datetime import datetime, date
from pathlib import Path
from typing import Iterable, List, Optional

DB_FILE = Path(__file__).with_name("tasks.db")
ISO_FORMAT = "%Y-%m-%d"
UNSET = object()


@dataclass
class Task:
    """Dataclass representing a task record."""

    id: int
    title: str
    description: str
    priority: int
    status: str
    due_date: Optional[date]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    @property
    def is_overdue(self) -> bool:
        return self.status == "pending" and self.due_date is not None and self.due_date < date.today()


class TaskManager:
    """Class responsible for interacting with the tasks database."""

    def __init__(self, db_path: Path = DB_FILE) -> None:
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self) -> None:
        """Ensure the tasks table exists."""
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                priority INTEGER DEFAULT 2,
                status TEXT DEFAULT 'pending',
                due_date TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                completed_at TEXT
            )
            """
        )
        self.conn.commit()

    def add_task(self, title: str, description: str = "", priority: int = 2, due: Optional[date] = None) -> Task:
        now = datetime.utcnow()
        due_value = due.isoformat() if due else None
        cursor = self.conn.execute(
            """
            INSERT INTO tasks (title, description, priority, status, due_date, created_at, updated_at)
            VALUES (?, ?, ?, 'pending', ?, ?, ?)
            """,
            (title, description, priority, due_value, now.isoformat(), now.isoformat()),
        )
        self.conn.commit()
        return self.get_task(cursor.lastrowid)

    def get_task(self, task_id: int) -> Task:
        row = self.conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if row is None:
            raise ValueError(f"Task with id {task_id} does not exist.")
        return self._row_to_task(row)

    def list_tasks(
        self,
        status: Optional[str] = None,
        show_overdue_only: bool = False,
        include_completed: bool = False,
        sort: str = "due",
    ) -> List[Task]:
        conditions: List[str] = []
        params: List[object] = []

        if status:
            conditions.append("status = ?")
            params.append(status)
        elif not include_completed:
            conditions.append("status != 'completed'")

        if show_overdue_only:
            conditions.append("status = 'pending' AND due_date IS NOT NULL AND due_date < ?")
            params.append(date.today().isoformat())

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        sort_clause = {
            "due": "ORDER BY CASE WHEN due_date IS NULL THEN 1 ELSE 0 END, due_date",
            "priority": "ORDER BY priority, due_date",
            "created": "ORDER BY datetime(created_at) DESC",
        }.get(sort, "ORDER BY CASE WHEN due_date IS NULL THEN 1 ELSE 0 END, due_date")

        rows = self.conn.execute(
            f"SELECT * FROM tasks {where_clause} {sort_clause}"
        ).fetchall()
        return [self._row_to_task(row) for row in rows]

    def complete_task(self, task_id: int) -> Task:
        now = datetime.utcnow().isoformat()
        cursor = self.conn.execute(
            """
            UPDATE tasks
            SET status = 'completed', completed_at = ?, updated_at = ?
            WHERE id = ?
            """,
            (now, now, task_id),
        )
        if cursor.rowcount == 0:
            raise ValueError(f"Task with id {task_id} does not exist.")
        self.conn.commit()
        return self.get_task(task_id)

    def update_task(
        self,
        task_id: int,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[int] = None,
        due: object = UNSET,
        status: Optional[str] = None,
    ) -> Task:
        fields: List[str] = []
        params: List[object] = []

        if title is not None:
            fields.append("title = ?")
            params.append(title)
        if description is not None:
            fields.append("description = ?")
            params.append(description)
        if priority is not None:
            fields.append("priority = ?")
            params.append(priority)
        if due is not UNSET:
            if isinstance(due, date):
                fields.append("due_date = ?")
                params.append(due.isoformat())
            elif due is None:
                fields.append("due_date = ?")
                params.append(None)
            else:
                raise ValueError("Invalid value for due date.")
        if status is not None:
            if status not in {"pending", "completed"}:
                raise ValueError("status must be either 'pending' or 'completed'")
            fields.append("status = ?")
            params.append(status)
            if status == "completed":
                fields.append("completed_at = ?")
                params.append(datetime.utcnow().isoformat())
            else:
                fields.append("completed_at = ?")
                params.append(None)

        if not fields:
            raise ValueError("No fields specified for update.")

        fields.append("updated_at = ?")
        params.append(datetime.utcnow().isoformat())
        params.append(task_id)

        cursor = self.conn.execute(
            f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?",
            params,
        )
        if cursor.rowcount == 0:
            raise ValueError(f"Task with id {task_id} does not exist.")
        self.conn.commit()
        return self.get_task(task_id)

    def delete_task(self, task_id: int) -> None:
        cursor = self.conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        if cursor.rowcount == 0:
            raise ValueError(f"Task with id {task_id} does not exist.")
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def _row_to_task(self, row: sqlite3.Row) -> Task:
        due_date = datetime.fromisoformat(row["due_date"]).date() if row["due_date"] else None
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return Task(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            priority=row["priority"],
            status=row["status"],
            due_date=due_date,
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            completed_at=completed_at,
        )


def parse_due_date(value: Optional[str]) -> Optional[date]:
    if value is None:
        return None
    try:
        return datetime.strptime(value, ISO_FORMAT).date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid date '{value}'. Expected format YYYY-MM-DD."
        ) from exc


def priority_from_string(value: str) -> int:
    mapping = {"low": 3, "medium": 2, "high": 1}
    if value.isdigit():
        try:
            prio = int(value)
        except ValueError as exc:
            raise argparse.ArgumentTypeError("Priority must be an integer, 'low', 'medium', or 'high'.") from exc
        if prio < 1 or prio > 3:
            raise argparse.ArgumentTypeError("Priority must be between 1 (high) and 3 (low).")
        return prio
    if value.lower() not in mapping:
        raise argparse.ArgumentTypeError("Priority must be an integer, 'low', 'medium', or 'high'.")
    return mapping[value.lower()]


def format_tasks(tasks: Iterable[Task]) -> str:
    if not tasks:
        return "No tasks found."

    headers = ["ID", "Title", "Due", "Priority", "Status", "Overdue", "Description"]
    lines = [" | ".join(headers), "-" * 80]
    for task in tasks:
        due_str = task.due_date.isoformat() if task.due_date else "—"
        priority_str = {1: "High", 2: "Medium", 3: "Low"}.get(task.priority, str(task.priority))
        overdue = "Yes" if task.is_overdue else "No"
        lines.append(
            " | ".join(
                [
                    str(task.id),
                    task.title,
                    due_str,
                    priority_str,
                    task.status.capitalize(),
                    overdue,
                    task.description.strip() or "—",
                ]
            )
        )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Task Manager CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", help="Short title for the task")
    add_parser.add_argument("-d", "--description", default="", help="Optional description")
    add_parser.add_argument("--due", type=parse_due_date, help="Due date in YYYY-MM-DD format")
    add_parser.add_argument("-p", "--priority", type=priority_from_string, default=2, help="Priority as 1-3 or low/medium/high")

    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("--all", action="store_true", help="Include completed tasks")
    list_parser.add_argument("--completed", action="store_true", help="Show only completed tasks")
    list_parser.add_argument("--overdue", action="store_true", help="Show only overdue tasks")
    list_parser.add_argument(
        "--sort",
        choices=["due", "priority", "created"],
        default="due",
        help="Sort order",
    )

    complete_parser = subparsers.add_parser("complete", help="Mark a task as completed")
    complete_parser.add_argument("task_id", type=int, help="ID of the task to mark as completed")

    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("task_id", type=int, help="ID of the task to delete")

    update_parser = subparsers.add_parser("update", help="Update an existing task")
    update_parser.add_argument("task_id", type=int, help="ID of the task to update")
    update_parser.add_argument("--title", help="New title")
    update_parser.add_argument("--description", help="New description")
    update_parser.add_argument("--priority", type=priority_from_string, help="New priority")
    update_parser.add_argument("--due", type=parse_due_date, help="New due date (YYYY-MM-DD)")
    update_parser.add_argument("--clear-due", action="store_true", help="Remove the due date")
    update_parser.add_argument(
        "--status",
        choices=["pending", "completed"],
        help="Update status manually",
    )

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    manager = TaskManager()

    try:
        if args.command == "add":
            task = manager.add_task(args.title, args.description, args.priority, args.due)
            print(f"Created task #{task.id}: {task.title}")
        elif args.command == "list":
            status = "completed" if args.completed else None
            tasks = manager.list_tasks(
                status=status,
                show_overdue_only=args.overdue,
                include_completed=args.all,
                sort=args.sort,
            )
            print(format_tasks(tasks))
        elif args.command == "complete":
            task = manager.complete_task(args.task_id)
            print(f"Marked task #{task.id} as completed.")
        elif args.command == "delete":
            manager.delete_task(args.task_id)
            print(f"Deleted task #{args.task_id}.")
        elif args.command == "update":
            due_value: object = UNSET
            if args.clear_due:
                due_value = None
            elif args.due is not None:
                due_value = args.due
            task = manager.update_task(
                args.task_id,
                title=args.title,
                description=args.description,
                priority=args.priority,
                due=due_value,
                status=args.status,
            )
            print(f"Updated task #{task.id}.")
        else:
            parser.error("Unknown command")
            return 1
        return 0
    except ValueError as exc:
        parser.error(str(exc))
        return 1
    finally:
        manager.close()


if __name__ == "__main__":
    raise SystemExit(main())
