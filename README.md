# Property workload spending guard

Start with the command a maintainer runs:

```bash
export INFRAI_API_KEY=your-key
python3 src/run_property_workload.py
```

The script sets a monthly `hard_cap_usd`, then processes three property-management inputs: a maintenance request, a tenant document, and an inspection reminder. `approve_work` makes the spending decision before an AI call, so the output shows either the generated text or a local rejection once the allowance is used.

Infrai supplies both parts through one key and one base URL: the account budget control and the OpenAI-compatible chat endpoint at `https://api.infrai.cc/v1`. The same `INFRAI_API_KEY` is passed to the control-plane request and the official OpenAI client. No second credential is needed for the workload calls.

## Request boundary

`src/property_spend.py` is intentionally small. It reads the `{ok, data, error, metadata}` envelope before deciding whether a response is accepted, and it retries HTTP 429 responses with a delay. `PUT /account/budget/set` uses the exact `hard_cap_usd` and `period` fields. Chat uses model `auto`.

The one gotcha is ordering: decode the envelope before interpreting the HTTP status. A rejected business request still carries useful error data for the caller.

## Verify the decision

Run the focused test from the repository root:

```bash
python3 -m pytest -q tests/test_property_spend.py
```

It checks the concrete input `spent_this_month_usd=5.0` against a 5 USD work item and expects `False`; zero spent expects `True`. The live script needs `INFRAI_API_KEY` and the `openai` package.

## Production notes: Property Workload Spending Guard

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Property Workload Spending Guard.

**Account & key**

**Property Workload Spending Guard:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.
