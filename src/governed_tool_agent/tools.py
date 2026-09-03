"""Typed tool registry and in-memory mock executors."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .contracts import DeleteCustomer, LookupOrder, ProposedAction, ToolResult, TypedAction


class ValidationError(ValueError):
    pass


Executor = Callable[[TypedAction], ToolResult]


@dataclass(frozen=True)
class RegisteredTool:
    parse: Callable[[dict[str, Any]], TypedAction]
    execute: Executor


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, RegisteredTool] = {}

    def register(self, name: str, tool: RegisteredTool) -> None:
        if name in self._tools:
            raise ValueError(f"Tool already registered: {name}")
        self._tools[name] = tool

    def validate(self, proposed: ProposedAction) -> TypedAction:
        try:
            tool = self._tools[proposed.tool_name]
        except KeyError as error:
            raise ValidationError(f"Unknown tool: {proposed.tool_name}") from error
        return tool.parse(proposed.arguments)

    def execute(self, action: TypedAction) -> ToolResult:
        return self._tools[tool_name_for(action)].execute(action)


def tool_name_for(action: TypedAction) -> str:
    if isinstance(action, LookupOrder):
        return "lookup_order"
    if isinstance(action, DeleteCustomer):
        return "delete_customer"
    raise TypeError(f"Unsupported action type: {type(action).__name__}")


def _required_string(arguments: dict[str, Any], field: str) -> str:
    value = arguments.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field} must be a non-empty string")
    if set(arguments) != {field}:
        raise ValidationError(f"Expected only {field}")
    return value


def parse_lookup_order(arguments: dict[str, Any]) -> LookupOrder:
    return LookupOrder(order_id=_required_string(arguments, "order_id"))


def parse_delete_customer(arguments: dict[str, Any]) -> DeleteCustomer:
    return DeleteCustomer(customer_id=_required_string(arguments, "customer_id"))


class MockLookupOrder:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, action: TypedAction) -> ToolResult:
        assert isinstance(action, LookupOrder)
        self.calls += 1
        return ToolResult("lookup_order", {"order_id": action.order_id, "status": "processing"})


class MockDeleteCustomer:
    """A sentinel mock: policy must prevent this executor from being called."""

    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, action: TypedAction) -> ToolResult:
        assert isinstance(action, DeleteCustomer)
        self.calls += 1
        return ToolResult("delete_customer", {"customer_id": action.customer_id, "deleted": True})


def default_registry(lookup: MockLookupOrder, delete: MockDeleteCustomer) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register("lookup_order", RegisteredTool(parse_lookup_order, lookup))
    registry.register("delete_customer", RegisteredTool(parse_delete_customer, delete))
    return registry
