"""Command-line demo for controlled action execution."""

import argparse
import json

from .planner import DeterministicPlanner
from .policy import PolicyEngine
from .runtime import GovernedRuntime
from .tools import MockDeleteCustomer, MockLookupOrder, default_registry


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a governed mock support action.")
    parser.add_argument("--scenario", choices=("happy", "denied"), default="happy")
    args = parser.parse_args()

    lookup, delete = MockLookupOrder(), MockDeleteCustomer()
    runtime = GovernedRuntime(default_registry(lookup, delete), PolicyEngine())
    proposed = DeterministicPlanner(args.scenario).propose("Resolve an order issue")
    outcome = runtime.run(proposed)
    print(json.dumps({
        "status": outcome.status,
        "tool_name": outcome.tool_name,
        "reason": outcome.reason,
        "result": outcome.result.payload if outcome.result else None,
    }, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
