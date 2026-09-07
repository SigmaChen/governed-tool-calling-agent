import unittest

from governed_tool_agent.planner import DeterministicPlanner
from governed_tool_agent.policy import PolicyEngine
from governed_tool_agent.runtime import GovernedRuntime, RunStatus
from governed_tool_agent.contracts import RuntimeContext
from governed_tool_agent.tools import (
    MockDeleteCustomer,
    MockDraftReply,
    MockLookupOrder,
    MockSendReply,
    default_registry,
)


class GovernedRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.lookup = MockLookupOrder()
        self.delete = MockDeleteCustomer()
        self.draft = MockDraftReply()
        self.send = MockSendReply()
        self.runtime = GovernedRuntime(
            default_registry(self.lookup, self.delete, self.draft, self.send),
            PolicyEngine(),
        )
        self.context = RuntimeContext("support", frozenset({"ORD-1001"}))

    def test_happy_path_validates_allows_and_executes_lookup(self) -> None:
        outcome = self.runtime.run(
            DeterministicPlanner("happy").propose("help"), self.context
        )

        self.assertEqual(outcome.status, RunStatus.EXECUTED)
        self.assertEqual(outcome.result.payload["status"], "processing")
        self.assertEqual(self.lookup.calls, 1)

    def test_denied_action_never_reaches_executor(self) -> None:
        outcome = self.runtime.run(
            DeterministicPlanner("denied").propose("help"), self.context
        )

        self.assertEqual(outcome.status, RunStatus.POLICY_DENIED)
        self.assertIn("prohibited", outcome.reason)
        self.assertEqual(self.delete.calls, 0)

    def test_cross_customer_lookup_never_reaches_executor(self) -> None:
        outcome = self.runtime.run(
            DeterministicPlanner("cross_customer").propose("help"), self.context
        )

        self.assertEqual(outcome.status, RunStatus.POLICY_DENIED)
        self.assertIn("authorized scope", outcome.reason)
        self.assertEqual(self.lookup.calls, 0)

    def test_authorized_reply_draft_executes(self) -> None:
        outcome = self.runtime.run(
            DeterministicPlanner("draft").propose("help"), self.context
        )

        self.assertEqual(outcome.status, RunStatus.EXECUTED)
        self.assertTrue(outcome.result.payload["drafted"])
        self.assertEqual(self.draft.calls, 1)

    def test_external_reply_requires_approval_without_execution(self) -> None:
        outcome = self.runtime.run(
            DeterministicPlanner("send").propose("help"), self.context
        )

        self.assertEqual(outcome.status, RunStatus.APPROVAL_REQUIRED)
        self.assertIn("require approval", outcome.reason)
        self.assertEqual(self.send.calls, 0)


if __name__ == "__main__":
    unittest.main()
