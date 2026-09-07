"""Explicit policy rules. No LLM interpretation belongs in this layer."""

from dataclasses import dataclass
from enum import StrEnum

from .contracts import (
    DeleteCustomer,
    DraftReply,
    LookupOrder,
    RuntimeContext,
    SendReply,
    TypedAction,
)


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
        if isinstance(action, (LookupOrder, DraftReply, SendReply)):
            if context.actor_role != "support":
                return PolicyDecision(Decision.DENY, "Role is not permitted to handle order support actions")
            if action.order_id not in context.allowed_order_ids:
                return PolicyDecision(
                    Decision.DENY,
                    "Order is outside the caller's authorized scope",
                )
            if isinstance(action, SendReply):
                return PolicyDecision(
                    Decision.REQUIRE_APPROVAL,
                    "External customer replies require approval",
                )
            if isinstance(action, DraftReply):
                return PolicyDecision(Decision.ALLOW, "Reply draft is allowed")
            return PolicyDecision(Decision.ALLOW, "Read-only order lookup is allowed")
        if isinstance(action, DeleteCustomer):
            return PolicyDecision(Decision.DENY, "Customer deletion is prohibited")
        return PolicyDecision(Decision.REQUIRE_APPROVAL, "Action requires human approval")
