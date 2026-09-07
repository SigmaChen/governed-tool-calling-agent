import unittest

from governed_tool_agent.planner import DeterministicPlanner
from governed_tool_agent.policy import PolicyEngine
from governed_tool_agent.runtime import GovernedRuntime, RunStatus
from governed_tool_agent.contracts import RuntimeContext
from governed_tool_agent.tools import MockDeleteCustomer, MockLookupOrder, default_registry


class GovernedRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.lookup = MockLookupOrder()
        self.delete = MockDeleteCustomer()
        self.runtime = GovernedRuntime(
            default_registry(self.lookup, self.delete), PolicyEngine()
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


if __name__ == "__main__":
    unittest.main()
