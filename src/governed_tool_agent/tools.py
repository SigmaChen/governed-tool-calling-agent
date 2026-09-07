"""Typed tool registry and in-memory mock executors."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .contracts import (
    DeleteCustomer,
    DraftReply,
    LookupOrder,
    ProposedAction,
    SendReply,
    ToolResult,
    TypedAction,
)


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
    if isinstance(action, DraftReply):
        return "draft_reply"
    if isinstance(action, SendReply):
        return "send_reply"
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


def _required_strings(arguments: dict[str, Any], *fields: str) -> dict[str, str]:
    if set(arguments) != set(fields):
        raise ValidationError(f"Expected only {', '.join(fields)}")
    values: dict[str, str] = {}
    for field in fields:
        value = arguments[field]
        if not isinstance(value, str) or not value.strip():
            raise ValidationError(f"{field} must be a non-empty string")
        values[field] = value
    return values


def parse_draft_reply(arguments: dict[str, Any]) -> DraftReply:
    values = _required_strings(arguments, "order_id", "message")
    return DraftReply(**values)


def parse_send_reply(arguments: dict[str, Any]) -> SendReply:
    values = _required_strings(arguments, "order_id", "message")
    return SendReply(**values)


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


class MockDraftReply:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, action: TypedAction) -> ToolResult:
        assert isinstance(action, DraftReply)
        self.calls += 1
        return ToolResult(
            "draft_reply",
            {"order_id": action.order_id, "message": action.message, "drafted": True},
        )


class MockSendReply:
    """A sentinel mock: this executor requires an approval flow before use."""

    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, action: TypedAction) -> ToolResult:
        assert isinstance(action, SendReply)
        self.calls += 1
        return ToolResult(
            "send_reply",
            {"order_id": action.order_id, "message": action.message, "sent": True},
        )


def default_registry(
    lookup: MockLookupOrder,
    delete: MockDeleteCustomer,
    draft: MockDraftReply,
    send: MockSendReply,
) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register("lookup_order", RegisteredTool(parse_lookup_order, lookup))
    registry.register("draft_reply", RegisteredTool(parse_draft_reply, draft))
    registry.register("send_reply", RegisteredTool(parse_send_reply, send))
    registry.register("delete_customer", RegisteredTool(parse_delete_customer, delete))
    return registry
