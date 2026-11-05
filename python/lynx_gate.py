"""Pre-trade check for a trading bot: one function, standard library only, Python 3.9+.

    from lynx_gate import check
    result = check("base", "0x...")
    if result.allow:
        ...  # your own trade logic

allow=True means only "no major red flags were found at this moment". It is not a promise and not advice.
Anything that goes wrong (network, limit, unknown chain) gives allow=False: a failed check never lets a trade through.
Chains: solana, eth, base, bsc, arb, polygon, op, avax. No key needed for a few checks an hour; api_key lifts the limits."""
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import List, Optional

URL = os.environ.get("LYNXCHECK_URL", "https://mintsieve.141-95-95-56.sslip.io")


@dataclass
class Check:
    allow: bool
    verdict: str                               # OK-NO-MAJOR-FLAGS, CAUTION, AVOID or NOT_CHECKED
    flags: List[str] = field(default_factory=list)
    note: Optional[str] = None


def check(chain: str, address: str, api_key: Optional[str] = None, timeout: float = 30.0, url: str = URL) -> Check:
    headers = {"Content-Type": "application/json", "User-Agent": "lynx-gate/1.0"}
    if api_key:
        headers["X-API-Key"] = api_key
    body = json.dumps({"items": [{"chain": chain, "address": address}]}).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url + "/v1/batch", body, headers), timeout=timeout) as r:
            item = json.load(r)["results"][0]
    except urllib.error.HTTPError as e:
        return Check(False, "NOT_CHECKED", note=f"HTTP {e.code}")
    except (OSError, ValueError, KeyError, IndexError, TypeError) as e:
        return Check(False, "NOT_CHECKED", note=type(e).__name__)
    verdict = item.get("verdict") if isinstance(item, dict) else None
    if not verdict:
        return Check(False, "NOT_CHECKED", note=str(item.get("error") if isinstance(item, dict) else "no verdict"))
    return Check(verdict == "OK-NO-MAJOR-FLAGS", verdict, list(item.get("flags") or []), item.get("note"))


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        sys.exit("usage: python lynx_gate.py <chain> <address>")
    print(check(sys.argv[1], sys.argv[2]))
