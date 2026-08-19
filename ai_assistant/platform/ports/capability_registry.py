"""Capability registry port."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from ai_assistant.domain.errors import InvalidToolCallError
from ai_assistant.platform.domain.task import CapabilityName


@dataclass(frozen=True, slots=True)
class CapabilityDefinition:
    name: CapabilityName
    description: str
    input_schema: Mapping[str, object]

    def __post_init__(self) -> None:
        if not isinstance(self.name, CapabilityName):
            try:
                object.__setattr__(self, "name", CapabilityName(self.name))
            except ValueError as exc:
                raise InvalidToolCallError("unknown capability.") from exc
        object.__setattr__(self, "input_schema", MappingProxyType(dict(self.input_schema)))


class CapabilityRegistry(ABC):
    @abstractmethod
    def names(self) -> tuple[CapabilityName, ...]:
        raise NotImplementedError

    @abstractmethod
    def definitions(self) -> tuple[CapabilityDefinition, ...]:
        raise NotImplementedError

    @abstractmethod
    def definition_for(self, capability: CapabilityName) -> CapabilityDefinition:
        raise NotImplementedError

    @abstractmethod
    def tool_name_for(self, capability: CapabilityName) -> str:
        raise NotImplementedError
