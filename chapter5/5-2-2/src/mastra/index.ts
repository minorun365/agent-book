import { Mastra } from "@mastra/core";
import { assistantAgent } from "./agents/assistantAgent";
// 今回作成したワークフロー
import { handsonWorkflow } from "./workflows/handson";


export const mastra = new Mastra({
  agents: { assistantAgent },
  // 作成したワークフローを追加
  workflows: { handsonWorkflow },
});
