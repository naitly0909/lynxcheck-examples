# Token checks for trading bots and AI agents

Copy-paste examples that check a token for known red flags before your bot swaps it. Solana and seven EVM chains, one HTTP call, no account and no key for a few checks an hour.

| Folder | For | Tested with |
|---|---|---|
| [`agent-rules/`](agent-rules/README.md) | Any AI agent that can trade: remote MCP plus rules for the system prompt | Official MCP Python client |
| [`python/`](python/lynx_gate.py) | Any Python bot, no dependencies | Python 3.14 |
| [`typescript/`](typescript/lynxGate.ts) | Any Node 18+ bot, no dependencies | Node 22 |
| [`langchain/`](langchain/lynx_tool.py) | LangChain tool | langchain-core 1.7.6 |
| [`solana-agent-kit/`](solana-agent-kit/lynxPlugin.ts) | Solana Agent Kit plugin | solana-agent-kit 2.0.10, zod 3 |
| [`elizaos/`](elizaos/lynxPlugin.ts) | elizaOS plugin | @elizaos/core 1.7.2 |

## Quick start

```python
from lynx_gate import check

result = check("base", "0x4200000000000000000000000000000000000006")
if result.allow:
    pass  # your own trade logic
else:
    print(result.verdict, result.flags, result.note)
```

The same call with curl:

```bash
curl -s https://mintsieve.141-95-95-56.sslip.io/v1/batch -H 'Content-Type: application/json' -d '{"items":[{"chain":"base","address":"0x4200000000000000000000000000000000000006"}]}'
```

## What the answer means

| Verdict | `allow` | Meaning |
|---|---|---|
| `OK-NO-MAJOR-FLAGS` | true | No major red flags at this moment. Contracts and pools change, so this is no promise. |
| `CAUTION` | false | Something needs a look, or the check is incomplete. A token we cannot score lands here, including most Solana tokens outside Pump.fun. |
| `AVOID` | false | Strong red flags, such as a failed sell simulation or a tax of 10% or more. |
| `NOT_CHECKED` | false | The check failed: network, rate limit or bad input. Added by these examples, not by the API. |

Every example fails closed: an error blocks the trade. Change that only if you have thought about what happens when the API is down.

## Limits

Without a key: up to 5 tokens per request, and fresh checks are limited per hour. Set `LYNXCHECK_API_KEY` (or pass `api_key`) to lift them. Details are on the [API page](https://mintsieve.141-95-95-56.sslip.io/api.html).

An LLM can skip a tool. If an agent can trade, call the check in the swap code as well.

Automated statistics, not financial advice. Data can be wrong or late.

MIT licence.
