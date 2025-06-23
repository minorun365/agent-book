import { Mastra } from '@mastra/core/mastra';
import { Agent } from '@mastra/core/agent';
import { createTool } from '@mastra/core/tools';
import { bedrock } from '@ai-sdk/amazon-bedrock';
import { z } from 'zod';

const addTool = createTool({
    id: '足し算ツール',
    description: '2つの数を足します。',
    inputSchema: z.object({
        a: z.number(),
        b: z.number(),
    }),
    execute: async ({ context }) => {
        return { result: context.a + context.b };
    },
});

const calculatorAgent = new Agent({
    name: '計算エージェント',
    instructions: 'ツールを使って足し算ができます。',
    model: bedrock('us.anthropic.claude-sonnet-4-20250514-v1:0'),
    tools: { addTool },
});

export const mastra = new Mastra({
    agents: { calculatorAgent },
});