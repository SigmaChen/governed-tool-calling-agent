"""Planner interfaces. Planners propose actions; they never execute tools."""

from typing import Protocol

from .contracts import ProposedAction


class Planner(Protocol):
    def propose(self, user_request: str) -> ProposedAction: ...


class DeterministicPlanner:
    """A repeatable fixture for the Day 1 demo and tests."""

    def __init__(self, scenario: str) -> None:
        self.scenario = scenario

    def propose(self, user_request: str) -> ProposedAction:
        del user_request  # A real adapter is intentionally out of scope.
        if self.scenario == "happy":
            return ProposedAction("lookup_order", {"order_id": "ORD-1001"})
        if self.scenario == "cross_customer":
            return ProposedAction("lookup_order", {"order_id": "ORD-2002"})
        if self.scenario == "denied":
            return ProposedAction("delete_customer", {"customer_id": "CUS-009"})
        raise ValueError(f"Unknown deterministic scenario: {self.scenario}")
