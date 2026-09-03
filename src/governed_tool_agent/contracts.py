"""Typed contracts at the boundary between a planner and runtime."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ProposedAction:
    """Untrusted structured data returned by a planner."""

    tool_name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class LookupOrder:
    order_id: str


@dataclass(frozen=True)
class DeleteCustomer:
    customer_id: str


TypedAction = LookupOrder | DeleteCustomer


@dataclass(frozen=True)
class ToolResult:
    tool_name: str
    payload: dict[str, Any]
