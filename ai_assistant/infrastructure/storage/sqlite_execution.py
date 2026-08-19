"""SQLite-backed execution store."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from ai_assistant.domain.errors import ExecutionStoreError
from ai_assistant.platform.domain.checkpoint import Checkpoint
from ai_assistant.platform.domain.execution import ExecutionRecord, ExecutionStatus
from ai_assistant.platform.domain.objective import Objective, ObjectiveStatus
from ai_assistant.platform.domain.plan import Plan, PlanStatus
from ai_assistant.platform.domain.task import CapabilityName, PlatformTask, PlatformTaskStatus
from ai_assistant.platform.ports.execution_store import ExecutionStore


class SQLiteExecutionStore(ExecutionStore):
    def __init__(self, database_path: str | Path) -> None:
        self._database_path = Path(database_path)
        self._initialize()

    def save_objective(self, objective: Objective) -> None:
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT OR REPLACE INTO execution_objectives
                    (objective_id, description, status, success_criteria)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        objective.objective_id,
                        objective.description,
                        objective.status.value,
                        json.dumps(objective.success_criteria),
                    ),
                )
        except sqlite3.Error as exc:
            raise ExecutionStoreError("Failed to persist execution objective.") from exc

    def load_objective(self, objective_id: str) -> Objective | None:
        try:
            with self._connect() as connection:
                row = connection.execute(
                    """
                    SELECT objective_id, description, status, success_criteria
                    FROM execution_objectives WHERE objective_id = ?
                    """,
                    (objective_id,),
                ).fetchone()
        except sqlite3.Error as exc:
            raise ExecutionStoreError("Failed to load execution objective.") from exc
        if row is None:
            return None
        return Objective(row[0], row[1], ObjectiveStatus(row[2]), tuple(json.loads(row[3])))

    def save_plan(self, plan: Plan) -> None:
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT OR REPLACE INTO execution_plans
                    (plan_id, objective_id, status) VALUES (?, ?, ?)
                    """,
                    (plan.plan_id, plan.objective_id, plan.status.value),
                )
                connection.execute("DELETE FROM execution_tasks WHERE plan_id = ?", (plan.plan_id,))
                connection.executemany(
                    """
                    INSERT INTO execution_tasks
                    (plan_id, task_id, objective_id, description, capability, arguments, dependencies, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        (
                            plan.plan_id,
                            task.task_id,
                            task.objective_id,
                            task.description,
                            task.capability.value,
                            json.dumps(dict(task.arguments)),
                            json.dumps(task.dependencies),
                            task.status.value,
                        )
                        for task in plan.tasks
                    ],
                )
        except sqlite3.Error as exc:
            raise ExecutionStoreError("Failed to persist execution plan.") from exc

    def load_plan(self, plan_id: str) -> Plan | None:
        try:
            with self._connect() as connection:
                plan_row = connection.execute(
                    "SELECT plan_id, objective_id, status FROM execution_plans WHERE plan_id = ?",
                    (plan_id,),
                ).fetchone()
                task_rows = connection.execute(
                    """
                    SELECT task_id, objective_id, description, capability, arguments, dependencies, status
                    FROM execution_tasks WHERE plan_id = ? ORDER BY rowid ASC
                    """,
                    (plan_id,),
                ).fetchall()
        except sqlite3.Error as exc:
            raise ExecutionStoreError("Failed to load execution plan.") from exc
        if plan_row is None:
            return None
        tasks = tuple(_task_from_row(row) for row in task_rows)
        return Plan(plan_row[0], plan_row[1], tasks, PlanStatus(plan_row[2]))

    def save_execution(self, execution: ExecutionRecord) -> None:
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT OR REPLACE INTO executions
                    (execution_id, objective_id, plan_id, status, started_at, ended_at, error_code)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        execution.execution_id,
                        execution.objective_id,
                        execution.plan_id,
                        execution.status.value,
                        _datetime_to_text(execution.started_at),
                        _datetime_to_text(execution.ended_at),
                        execution.error_code,
                    ),
                )
        except sqlite3.Error as exc:
            raise ExecutionStoreError("Failed to persist execution state.") from exc

    def load_execution(self, execution_id: str) -> ExecutionRecord | None:
        try:
            with self._connect() as connection:
                row = connection.execute(
                    """
                    SELECT execution_id, objective_id, plan_id, status, started_at, ended_at, error_code
                    FROM executions WHERE execution_id = ?
                    """,
                    (execution_id,),
                ).fetchone()
        except sqlite3.Error as exc:
            raise ExecutionStoreError("Failed to load execution state.") from exc
        if row is None:
            return None
        return ExecutionRecord(
            row[0],
            row[1],
            row[2],
            ExecutionStatus(row[3]),
            _datetime_from_text(row[4]),
            _datetime_from_text(row[5]),
            row[6],
        )

    def update_task_status(
        self,
        plan_id: str,
        task_id: str,
        status: PlatformTaskStatus,
    ) -> None:
        try:
            with self._connect() as connection:
                result = connection.execute(
                    """
                    UPDATE execution_tasks SET status = ?
                    WHERE plan_id = ? AND task_id = ?
                    """,
                    (status.value, plan_id, task_id),
                )
                if result.rowcount != 1:
                    raise ExecutionStoreError("Execution task not found.")
        except sqlite3.Error as exc:
            raise ExecutionStoreError("Failed to persist execution task state.") from exc

    def load_task_status(
        self,
        plan_id: str,
        task_id: str,
    ) -> PlatformTaskStatus | None:
        try:
            with self._connect() as connection:
                row = connection.execute(
                    """
                    SELECT status FROM execution_tasks
                    WHERE plan_id = ? AND task_id = ?
                    """,
                    (plan_id, task_id),
                ).fetchone()
        except sqlite3.Error as exc:
            raise ExecutionStoreError("Failed to load execution task state.") from exc
        return None if row is None else PlatformTaskStatus(row[0])

    def save_checkpoint(self, checkpoint: Checkpoint) -> None:
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT OR REPLACE INTO execution_checkpoints
                    (checkpoint_id, execution_id, task_id, metadata, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        checkpoint.checkpoint_id,
                        checkpoint.execution_id,
                        checkpoint.task_id,
                        json.dumps(dict(checkpoint.metadata)),
                        checkpoint.created_at.isoformat(),
                    ),
                )
        except sqlite3.Error as exc:
            raise ExecutionStoreError("Failed to persist execution checkpoint.") from exc

    def checkpoints_for_execution(self, execution_id: str) -> tuple[Checkpoint, ...]:
        try:
            with self._connect() as connection:
                rows = connection.execute(
                    """
                    SELECT checkpoint_id, execution_id, task_id, metadata, created_at
                    FROM execution_checkpoints
                    WHERE execution_id = ?
                    ORDER BY created_at ASC, checkpoint_id ASC
                    """,
                    (execution_id,),
                ).fetchall()
        except sqlite3.Error as exc:
            raise ExecutionStoreError("Failed to load execution checkpoints.") from exc
        return tuple(
            Checkpoint(row[0], row[1], row[2], json.loads(row[3]), datetime.fromisoformat(row[4]))
            for row in rows
        )

    def _initialize(self) -> None:
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self._connect() as connection:
                _create_schema(connection)
        except sqlite3.Error as exc:
            raise ExecutionStoreError("Failed to initialize execution store.") from exc

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._database_path)


def _create_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS execution_objectives (
            objective_id TEXT PRIMARY KEY,
            description TEXT NOT NULL,
            status TEXT NOT NULL,
            success_criteria TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS execution_plans (
            plan_id TEXT PRIMARY KEY,
            objective_id TEXT NOT NULL,
            status TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS execution_tasks (
            plan_id TEXT NOT NULL,
            task_id TEXT NOT NULL,
            objective_id TEXT NOT NULL,
            description TEXT NOT NULL,
            capability TEXT NOT NULL,
            arguments TEXT NOT NULL,
            dependencies TEXT NOT NULL,
            status TEXT NOT NULL,
            PRIMARY KEY (plan_id, task_id)
        );
        CREATE TABLE IF NOT EXISTS executions (
            execution_id TEXT PRIMARY KEY,
            objective_id TEXT NOT NULL,
            plan_id TEXT NOT NULL,
            status TEXT NOT NULL,
            started_at TEXT,
            ended_at TEXT,
            error_code TEXT
        );
        CREATE TABLE IF NOT EXISTS execution_checkpoints (
            checkpoint_id TEXT PRIMARY KEY,
            execution_id TEXT NOT NULL,
            task_id TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )


def _task_from_row(row: sqlite3.Row | tuple[object, ...]) -> PlatformTask:
    return PlatformTask(
        str(row[0]),
        str(row[1]),
        str(row[2]),
        CapabilityName(str(row[3])),
        json.loads(str(row[4])),
        tuple(json.loads(str(row[5]))),
        PlatformTaskStatus(str(row[6])),
    )


def _datetime_to_text(value: datetime | None) -> str | None:
    return None if value is None else value.isoformat()


def _datetime_from_text(value: str | None) -> datetime | None:
    return None if value is None else datetime.fromisoformat(value)
