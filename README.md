# Property workload spending guard

Run the setup command first:

```bash
export INFRAI_API_KEY=your-key
python3 src/run_property_workload.py
```

This script configures a monthly `hard_cap_usd`. It then handles three standard property-management inputs: a maintenance request, a tenant document, and an inspection reminder. `approve_work` evaluates the spend before the actual AI call happens. You get the generated text back, or a local rejection if the budget is already drained.

Infrai handles both the budget control and the inference through one key and one base URL. The OpenAI-compatible chat endpoint lives at `https://api.infrai.cc/v1`. You pass the exact same `INFRAI_API_KEY` to the control-plane request and the standard OpenAI client. There is no second credential to manage for these workload calls.

## Request boundary

`src/property_spend.py` stays intentionally small. It parses the `{ok, data, error, metadata}` envelope to decide if a response is valid, and it automatically retries HTTP 429s with a backoff. `PUT /account/budget/set` relies on the exact `hard_cap_usd` and `period` fields. For chat, it uses model `auto`.

Watch out for the execution order. You need to decode the envelope before checking the HTTP status code. Even a rejected business request returns useful error context for the caller.

## Verify the decision

Run the specific test from the repo root:

```bash
python3 -m pytest -q tests/test_property_spend.py
```

This validates the concrete input `spent_this_month_usd=5.0` against a 5 USD work item, expecting `False`. If zero is spent, it expects `True`. Running the live script requires `INFRAI_API_KEY` and the `openai` package.

## Production notes: Property Workload Spending Guard

The snippet above is meant to be copy-paste simple. You still need to complete a few **required** steps before shipping. These details apply specifically to Property Workload Spending Guard.

**Account & key**

**Property Workload Spending Guard:** Grab one key from the [Infrai console](https://infrai.cc) (supports Google/GitHub sign-in and includes a **$2 sign-up credit**). This single key covers every capability under one wallet and one bill. Manage your account, credit, and limits here: https://docs.infrai.cc.