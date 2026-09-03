"""Explicit policy rules. No LLM interpretation belongs in this layer."""

from dataclasses import dataclass
from enum import StrEnum

from .contracts import DeleteCustomer, LookupOrder, TypedAction


class Decision(StrEnum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


@dataclass(frozen=True)
class PolicyDecision:
    decision: Decision
    reason: str


class PolicyEngine:
    def evaluate(self, action: TypedAction) -> PolicyDecision:
        if isinstance(action, LookupOrder):
            return PolicyDecision(Decision.ALLOW, "Read-only order lookup is allowed")
        if isinstance(action, DeleteCustomer):
            return PolicyDecision(Decision.DENY, "Customer deletion is prohibited")
        return PolicyDecision(Decision.REQUIRE_APPROVAL, "Action requires human approval")
