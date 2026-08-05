"""Planner port."""

from abc import ABC, abstractmethod

from ai_assistant.platform.domain.objective import Objective
from ai_assistant.platform.domain.plan import Plan


class Planner(ABC):
    @abstractmethod
    def create_plan(self, objective: Objective) -> Plan:
        raise NotImplementedError

