# Governed Tool-Calling Agent

An auditable runtime policy decision point between an AI planner and a tool
executor. A model may propose a structured action, but typed validation,
runtime context, and configurable policy rules determine whether the action is
executed, denied, or sent for approval.

## Why not simply hide unsafe tools?

Tool registration is a useful static boundary: an agent cannot call a tool that
is not exposed to it. It is not enough for tools that must be available but
need different decisions for different invocations. For example, a support
agent may use `lookup_order`, while trusted caller scope and role determine
whether this particular lookup can proceed.

```text
Planner proposes a typed action
  + RuntimeContext (role, approval state, request metadata)
  + Tool registry (known tool and valid arguments)
  + Configurable policy (limits and explicit rules)
        ↓
allow / deny / require_approval decision
        ↓
mock executor runs only for allow
        ↓
trace records the action, context, policy version, reason, and outcome
```

This runtime is an enforcement point, not a prompt convention: a denied action
never reaches its executor.

## Phase 1 demo

The current demo uses a deterministic planner rather than a live LLM so that
the execution boundary is repeatable in tests. A future LLM adapter will have
the same limited responsibility: return a `ProposedAction`; it does not receive
direct executor access.

- `lookup_order(order_id)` is validated, allowed, and run against an in-memory
  mock.
- A lookup for an order outside the trusted caller scope is policy-denied before
  the mock tool runs.
- `draft_reply(order_id, message)` is allowed for an authorized order, while
  `send_reply(order_id, message)` stops at `approval_required`.
- `delete_customer(customer_id)` is structurally valid but policy-denied; its
  mock executor is never called.

## Run it

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
python -m governed_tool_agent.cli --scenario happy
python -m governed_tool_agent.cli --scenario cross_customer
python -m governed_tool_agent.cli --scenario draft
python -m governed_tool_agent.cli --scenario send
python -m governed_tool_agent.cli --scenario denied
```

## Scope and limitations

All tools are in-memory mocks. This version has no network calls, real customer
or payment data, credentials, authentication, web UI, MCP integration, or
general-purpose agent framework. Runtime policy complements rather than
replaces authorization enforced by a real downstream tool service.
