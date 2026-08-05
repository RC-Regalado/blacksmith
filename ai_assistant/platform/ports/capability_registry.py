"""Capability registry port."""

from abc import ABC, abstractmethod


class CapabilityRegistry(ABC):
    @abstractmethod
    def names(self) -> tuple[str, ...]:
        raise NotImplementedError

