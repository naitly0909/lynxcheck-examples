/**
 * Solana Agent Kit plugin (checked against solana-agent-kit 2.0.10): gives the agent a LYNX_CHECK_TOKEN action and an agent.methods.lynxCheck() method.
 *
 *   const agent = new SolanaAgentKit(wallet, rpcUrl, {}).use(LynxPlugin);
 *   const result = await agent.methods.lynxCheck(mint);
 *
 * Needs zod 3 (solana-agent-kit does not accept zod 4 schemas). Copy typescript/lynxGate.ts next to this file. Call the check in your own swap code too: an LLM can skip a tool.
 */
import type { Action, Plugin, SolanaAgentKit } from "solana-agent-kit";
import { z } from "zod";
import { lynxCheck } from "./lynxGate";

const checkAction: Action = {
  name: "LYNX_CHECK_TOKEN",
  similes: ["check token risk", "check token before swap", "token red flags"],
  description: "Checks a Solana token for known red flags before a swap. allow=false means do not continue without asking the user. allow=true is no promise that the token is fine.",
  examples: [[{
    input: { mint: "So11111111111111111111111111111111111111112" },
    output: { allow: false, verdict: "CAUTION", flags: [] },
    explanation: "The token has no score, so the swap should wait for the user.",
  }]],
  schema: z.object({ mint: z.string().min(32).max(44) }),
  handler: async (_agent: SolanaAgentKit, input: Record<string, any>) => lynxCheck("solana", input.mint),
};

export const LynxPlugin = {
  name: "lynxcheck",
  methods: { lynxCheck: async (mint: string) => lynxCheck("solana", mint) },
  actions: [checkAction],
  initialize() {},
} satisfies Plugin;
