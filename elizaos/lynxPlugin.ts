/**
 * elizaOS plugin (checked against @elizaos/core 1.7.2): the agent answers token questions with the LYNX_CHECK_TOKEN action.
 * Add lynxPlugin to the `plugins` list of your agent. Copy typescript/lynxGate.ts next to this file.
 * Call lynxCheck() in your own swap code too: an LLM can skip an action.
 */
import type { Action, ActionResult, Plugin } from "@elizaos/core";
import { lynxCheck } from "./lynxGate";

const EVM = /\b0x[a-fA-F0-9]{40}\b/;
const SOLANA = /\b[1-9A-HJ-NP-Za-km-z]{32,44}\b/;
const CHAINS = ["solana", "eth", "base", "bsc", "arb", "polygon", "op", "avax"];

function findToken(text: string): { chain: string; address: string } | null {
  const evm = text.match(EVM)?.[0];
  if (evm) return { chain: CHAINS.find((c) => new RegExp(`\\b${c}\\b`, "i").test(text) && c !== "solana") ?? "eth", address: evm };
  const sol = text.match(SOLANA)?.[0];
  return sol ? { chain: "solana", address: sol } : null;
}

const checkToken: Action = {
  name: "LYNX_CHECK_TOKEN",
  similes: ["CHECK_TOKEN", "TOKEN_RED_FLAGS"],
  description: "Checks a token address for known red flags on Solana or an EVM chain. Use before any swap. No flags found is no promise that the token is fine.",
  validate: async (_runtime, message) => findToken(message.content.text ?? "") !== null,
  handler: async (_runtime, message, _state, _options, callback): Promise<ActionResult> => {
    const token = findToken(message.content.text ?? "");
    if (!token) return { success: false, text: "No token address found." };
    const result = await lynxCheck(token.chain, token.address);
    const flags = result.flags.length ? ` Flags: ${result.flags.join(", ")}.` : "";
    const text = `${token.address} on ${token.chain}: ${result.verdict}.${flags} Automated check, not advice.`;
    await callback?.({ text, actions: ["LYNX_CHECK_TOKEN"] });
    return { success: result.verdict !== "NOT_CHECKED", text, data: { ...result } };
  },
  examples: [[
    { name: "{{user}}", content: { text: "check 0xdAC17F958D2ee523a2206206994597C13D831ec7 on eth" } },
    { name: "{{agent}}", content: { text: "Checking it for red flags.", actions: ["LYNX_CHECK_TOKEN"] } },
  ]],
};

export const lynxPlugin: Plugin = { name: "lynxcheck", description: "Token red-flag checks before a swap", actions: [checkToken] };
