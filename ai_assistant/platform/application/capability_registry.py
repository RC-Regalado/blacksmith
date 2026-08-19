"""Capability registry backed by the existing tool catalog."""

from collections.abc import Mapping

from ai_assistant.application.ports.tools import ToolCatalog
from ai_assistant.application.tool_catalog import (
    BUILD_PROJECT,
    FILE_METADATA,
    GIT_DIFF,
    GIT_STATUS,
    LIST_DIRECTORY,
    READ_FILE,
    RUN_TESTS,
    SEARCH_TEXT,
)
from ai_assistant.domain.errors import InvalidToolCallError
from ai_assistant.platform.domain.task import CapabilityName
from ai_assistant.platform.ports.capability_registry import (
    CapabilityDefinition,
    CapabilityRegistry,
)


_CAPABILITY_TO_TOOL: Mapping[CapabilityName, str] = {
    CapabilityName.INSPECT_DIRECTORY: LIST_DIRECTORY,
    CapabilityName.READ_FILE: READ_FILE,
    CapabilityName.INSPECT_FILE_METADATA: FILE_METADATA,
    CapabilityName.SEARCH_TEXT: SEARCH_TEXT,
    CapabilityName.INSPECT_GIT_STATUS: GIT_STATUS,
    CapabilityName.INSPECT_GIT_DIFF: GIT_DIFF,
    CapabilityName.RUN_TESTS: RUN_TESTS,
    CapabilityName.BUILD_PROJECT: BUILD_PROJECT,
}


class StaticCapabilityRegistry(CapabilityRegistry):
    def __init__(self, catalog: ToolCatalog) -> None:
        self._catalog = catalog

    def names(self) -> tuple[CapabilityName, ...]:
        return tuple(_CAPABILITY_TO_TOOL)

    def definitions(self) -> tuple[CapabilityDefinition, ...]:
        return tuple(self.definition_for(name) for name in self.names())

    def definition_for(self, capability: CapabilityName) -> CapabilityDefinition:
        tool_name = self.tool_name_for(capability)
        tool = self._catalog.definition_for(tool_name)
        return CapabilityDefinition(
            name=capability,
            description=tool.description,
            input_schema=tool.input_schema,
        )

    def tool_name_for(self, capability: CapabilityName) -> str:
        try:
            return _CAPABILITY_TO_TOOL[_coerce_capability(capability)]
        except KeyError as exc:
            raise InvalidToolCallError("unknown capability.") from exc


def _coerce_capability(capability: CapabilityName) -> CapabilityName:
    if isinstance(capability, CapabilityName):
        return capability
    try:
        return CapabilityName(capability)
    except ValueError as exc:
        raise InvalidToolCallError("unknown capability.") from exc
