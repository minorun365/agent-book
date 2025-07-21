import { VoltAgent, Agent, createTool } from "@voltagent/core";
import { VercelAIProvider } from "@voltagent/vercel-ai";
import { bedrock } from "@ai-sdk/amazon-bedrock";
import { z } from "zod";

// ツールを定義
const addTool = createTool({
    name: "add_tool",
    description: "2つの数を足します。",
    parameters: z.object({
        a: z.number().describe("最初の数"),
        b: z.number().describe("2番目の数"),
    }),
    execute: async ({ a, b }: { a: number; b: number }) => {
        return { result: a + b };
    },
});

// エージェントを定義
const agent = new Agent({
    name: "計算エージェント",
    instructions: "ツールを使って足し算ができます。",
    llm: new VercelAIProvider(),
    model: bedrock("us.anthropic.claude-sonnet-4-20250514-v1:0"),
    tools: [addTool],
});

// VoltAgentインスタンスを作成
new VoltAgent({
    agents: {
        agent,
    },
});