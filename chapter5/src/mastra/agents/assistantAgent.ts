import { Agent } from "@mastra/core/agent";
import { getBedrockModel } from "../../../lib/aws-config";

const model = await getBedrockModel();

export const assistantAgent = new Agent({
  name: "assistant",
  instructions:
      "あなたは親切で知識豊富なAIアシスタントです。ユーザーの質問に対して、わかりやすく丁寧に回答してください。必要に応じてGitHubツールを使用してイシューの作成を行うことができます。",
  model: model,
});
