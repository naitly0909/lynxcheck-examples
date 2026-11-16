#!/usr/bin/env python3
"""Your own trade journal through the LynxCheck remote MCP server, no dependencies.

The journal is the trades of the wallets you added in the LynxCheck Telegram bot (/journal <address>) or on the website.
The account key names your journal. Get it in the bot: /journal, then "Key for agents" (or on the account page). It only reads.

    export LYNXCHECK_API_KEY=ms_...
    python3 journal_mcp.py                 # summary of the last 7 days and the card of the token with the largest loss
    python3 journal_mcp.py all             # whole plan window (free: last 30 days and 100 trades; Premium: everything)
    python3 journal_mcp.py 30d <mint>      # card of one token

Same three tools inside an agent: add https://mintsieve.141-95-95-56.sslip.io/v1/mcp as a remote MCP server and send the key as the X-API-Key header.
Past trades, not a recommendation. Information, not tax advice."""
import json, os, sys, urllib.request

URL = os.environ.get("LYNXCHECK_URL", "https://mintsieve.141-95-95-56.sslip.io").rstrip("/") + "/v1/mcp"
KEY = os.environ.get("LYNXCHECK_API_KEY", "")


def call(tool, args):
    """One MCP tools/call over Streamable HTTP (JSON answers). -> (is_error, parsed result)."""
    body = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": tool, "arguments": args}}
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json", **({"X-API-Key": KEY} if KEY else {})})
    with urllib.request.urlopen(req, timeout=60) as r: res = json.load(r)["result"]
    text = res["content"][0]["text"]
    try: return bool(res.get("isError")), json.loads(text)
    except ValueError: return True, {"error": text}


def usd(x): return "n/a" if x is None else f"{x:+,.2f} USD"


def main():
    period = sys.argv[1] if len(sys.argv) > 1 else "7d"; mint = sys.argv[2] if len(sys.argv) > 2 else None
    err, s = call("journal_summary", {"period": period})
    if err: print(s.get("error", s)); return 1
    t = s["totals"]
    print(f"Journal, {period}: {t['trades']} trades, result {usd(t['realized_pnl_usd'])}, fees {usd(t['fees_usd'])}")
    rows = [x for x in s["tokens"] if x["buys"] or x["sells"]]
    for x in sorted(rows, key=lambda x: x["realized_usd"])[:10]:
        print(f"  {x['mint'][:8]}…  {x['buys']} buys / {x['sells']} sells  {usd(x['realized_usd'])}  verdict {x.get('verdict') or 'unknown'}")
    target = mint or (min(rows, key=lambda x: x["realized_usd"])["mint"] if rows else None)
    if not target: print("No priced trades in this window."); return 0
    err, c = call("journal_token", {"mint": target})
    if err: print(c.get("error", c)); return 1
    sm = c["summary"]
    print(f"\nToken card {target[:8]}…: {sm['status']}, {sm['buys']} buys for {usd(sm['bought_usd'])}, {sm['sells']} sells for {usd(sm['sold_usd'])}, result {usd(sm['realized_usd'])}"
          + (f" ({sm['realized_pct']:+.1f}% on the sold part)" if sm.get("realized_pct") is not None else ""))
    for p in c["sells"]:
        print(f"  sell {p['share_pct']}% of the position at {p['unit']:.6g}" + (f", {p['vs_avg_pct']:+.1f}% vs. average cost" if p.get("vs_avg_pct") is not None else "") + f", {usd(p['pnl_usd'])}")
    for n in c["notes"]: print("  note:", json.dumps(n))
    print("\nPast trades, not a recommendation."); return 0


if __name__ == "__main__": sys.exit(main())
