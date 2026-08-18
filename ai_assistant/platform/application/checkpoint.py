"""Logical checkpoint service."""

from collections.abc import Callable, Mapping
from datetime import UTC, datetime
import logging
from types import MappingProxyType
from uuid import uuid4

from ai_assistant.domain.errors import InvalidToolCallError
from ai_assistant.platform.domain.checkpoint import Checkpoint
from ai_assistant.platform.domain.task import PlatformTaskStatus
from ai_assistant.platform.ports.execution_store import ExecutionStore


logger = logging.getLogger(__name__)


class CheckpointService:
    def __init__(
        self,
        store: ExecutionStore,
        id_factory: Callable[[], str] | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._store = store
        self._id_factory = id_factory or (lambda: str(uuid4()))
        self._clock = clock or (lambda: datetime.now(UTC))

    def checkpoint_task(
        self,
        execution_id: str,
        task_id: str,
        status: PlatformTaskStatus,
        metadata: Mapping[str, object],
    ) -> Checkpoint:
        if status != PlatformTaskStatus.SUCCEEDED:
            raise InvalidToolCallError("only successful tasks can be checkpointed.")
        checkpoint = Checkpoint(
            self._id_factory(),
            execution_id,
            task_id,
            metadata,
            self._clock(),
        )
        self._store.save_checkpoint(checkpoint)
        logger.info(
            "checkpoint saved execution_id=%s task_id=%s checkpoint_id=%s",
            checkpoint.execution_id,
            checkpoint.task_id,
            checkpoint.checkpoint_id,
        )
        return checkpoint

    def restore_metadata(self, execution_id: str) -> Mapping[str, object]:
        checkpoints = self._store.checkpoints_for_execution(execution_id)
        if not checkpoints:
            return MappingProxyType({})
        return checkpoints[-1].metadata
