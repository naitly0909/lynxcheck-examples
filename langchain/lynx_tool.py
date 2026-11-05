"""LangChain tool: pip install langchain-core, copy python/lynx_gate.py next to this file.

    from lynx_tool import lynx_check_token
    agent = create_agent(model, tools=[lynx_check_token, your_swap_tool])

Call lynx_gate.check() in your own swap tool too: an LLM can skip a tool."""
from dataclasses import asdict

from langchain_core.tools import tool

from lynx_gate import check


@tool
def lynx_check_token(chain: str, address: str) -> dict:
    """Check a token for known red flags before a swap. chain is one of solana, eth, base, bsc, arb, polygon, op, avax.
    allow=false means do not continue without asking the user. allow=true is no promise that the token is fine."""
    return asdict(check(chain, address))
