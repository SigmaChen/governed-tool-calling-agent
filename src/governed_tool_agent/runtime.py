"""Orchestration that makes validation and policy mandatory before execution."""

from dataclasses import dataclass
from enum import StrEnum

from .contracts import ProposedAction, ToolResult
from .policy import Decision, PolicyEngine
from .tools import ToolRegistry, ValidationError, tool_name_for


class RunStatus(StrEnum):
    EXECUTED = "executed"
    VALIDATION_ERROR = "validation_error"
    POLICY_DENIED = "policy_denied"
    APPROVAL_REQUIRED = "approval_required"


@dataclass(frozen=True)
class RunResult:
    status: RunStatus
    tool_name: str
    reason: str | None = None
    result: ToolResult | None = None


class GovernedRuntime:
    def __init__(self, registry: ToolRegistry, policy: PolicyEngine) -> None:
        self.registry = registry
        self.policy = policy

    def run(self, proposed: ProposedAction) -> RunResult:
        try:
            action = self.registry.validate(proposed)
        except ValidationError as error:
            return RunResult(RunStatus.VALIDATION_ERROR, proposed.tool_name, str(error))

        decision = self.policy.evaluate(action)
        if decision.decision is Decision.DENY:
            return RunResult(RunStatus.POLICY_DENIED, tool_name_for(action), decision.reason)
        if decision.decision is Decision.REQUIRE_APPROVAL:
            return RunResult(RunStatus.APPROVAL_REQUIRED, tool_name_for(action), decision.reason)
        return RunResult(RunStatus.EXECUTED, tool_name_for(action), result=self.registry.execute(action))
