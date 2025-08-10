import { Mastra } from "@mastra/core";
import { assistantAgent } from "./agents/assistantAgent";

export const mastra = new Mastra({
  agents: { assistantAgent },
});
