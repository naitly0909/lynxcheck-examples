/**
 * Pre-trade check for a trading bot or agent. No dependencies, Node 18+.
 *
 *   const result = await lynxCheck("solana", mint);
 *   if (result.allow) { ... your own trade logic ... }
 *
 * allow=true means only "no major red flags were found at this moment". It is not a promise and not advice.
 * Anything that goes wrong gives allow=false: a failed check never lets a trade through.
 * Chains: solana, eth, base, bsc, arb, polygon, op, avax. No key needed for a few checks an hour.
 */
export const LYNX_URL = process.env.LYNXCHECK_URL ?? "https://mintsieve.141-95-95-56.sslip.io";

export type LynxVerdict = "OK-NO-MAJOR-FLAGS" | "CAUTION" | "AVOID" | "NOT_CHECKED";
export interface LynxResult { allow: boolean; verdict: LynxVerdict; flags: string[]; note?: string }

export async function lynxCheck(chain: string, address: string, apiKey = process.env.LYNXCHECK_API_KEY, timeoutMs = 30_000): Promise<LynxResult> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (apiKey) headers["X-API-Key"] = apiKey;
  try {
    const res = await fetch(`${LYNX_URL}/v1/batch`, { method: "POST", headers, body: JSON.stringify({ items: [{ chain, address }] }), signal: AbortSignal.timeout(timeoutMs) });
    if (!res.ok) return { allow: false, verdict: "NOT_CHECKED", flags: [], note: `HTTP ${res.status}` };
    const item = ((await res.json()) as { results?: Array<{ verdict?: LynxVerdict; flags?: string[]; note?: string; error?: string }> }).results?.[0];
    if (!item?.verdict) return { allow: false, verdict: "NOT_CHECKED", flags: [], note: item?.error ?? "no verdict" };
    return { allow: item.verdict === "OK-NO-MAJOR-FLAGS", verdict: item.verdict, flags: item.flags ?? [], note: item.note };
  } catch (e) {
    return { allow: false, verdict: "NOT_CHECKED", flags: [], note: e instanceof Error ? e.name : "error" };
  }
}
