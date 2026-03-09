import { bedrock } from '@ai-sdk/amazon-bedrock';
import { Mastra } from '@mastra/core';
import { Agent } from '@mastra/core/agent';
import { Memory } from '@mastra/memory';
import { LibSQLStore } from '@mastra/libsql';

// 計画保持のためのメモリを作成
const memory = new Memory({
  storage: new LibSQLStore({
    id: 'mastra-storage',
    url: 'file:../mastra.db',
  }),
});

// 調査エージェントを作成
const lister = new Agent({
  id: 'lister',
  name: 'lister',
  instructions: '調査を行い、箇条書きで簡潔に回答します。',
  description: '調査を行い、箇条書きで簡潔に回答します。',
  model: bedrock('us.anthropic.claude-sonnet-4-20250514-v1:0'),
});

// 執筆エージェントを作成
const writer = new Agent({
  id: 'writer',
  name: 'writer',
  description: '調査素材をマージして完全なレポートを執筆します。',
  instructions: '調査素材をマージして完全なレポートを執筆します。',
  model: bedrock('us.anthropic.claude-sonnet-4-20250514-v1:0'),
});

// オーケストレーターエージェントを作成（エージェントネットワーク機能を内包）
const orchestrator = new Agent({
  id: 'orchestrator',
  name: 'orchestrator',
  instructions: '企業について調査できます。また、調査素材をマージしてレポートを執筆できます',
  model: bedrock('us.anthropic.claude-sonnet-4-20250514-v1:0'),
  agents: { lister, writer },
  memory: memory,
});

// Mastraインスタンスを作成
export const mastra = new Mastra({
  agents: { lister, writer, orchestrator },
});