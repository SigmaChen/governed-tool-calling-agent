"""Explicit policy rules. No LLM interpretation belongs in this layer."""

from dataclasses import dataclass
from enum import StrEnum

from .contracts import DeleteCustomer, LookupOrder, RuntimeContext, TypedAction


class Decision(StrEnum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


@dataclass(frozen=True)
class PolicyDecision:
    decision: Decision
    reason: str


class PolicyEngine:
    def evaluate(self, action: TypedAction, context: RuntimeContext) -> PolicyDecision:
        if isinstance(action, LookupOrder):
            if context.actor_role != "support":
                return PolicyDecision(Decision.DENY, "Role is not permitted to look up orders")
            if action.order_id not in context.allowed_order_ids:
                return PolicyDecision(
                    Decision.DENY,
                    "Order is outside the caller's authorized scope",
                )
            return PolicyDecision(Decision.ALLOW, "Read-only order lookup is allowed")
        if isinstance(action, DeleteCustomer):
            return PolicyDecision(Decision.DENY, "Customer deletion is prohibited")
        return PolicyDecision(Decision.REQUIRE_APPROVAL, "Action requires human approval")
