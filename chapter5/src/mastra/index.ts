import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";
import { Mastra } from "@mastra/core";
import { assistantAgent } from "./agents/assistantAgent";
import { handsonWorkflow } from "./workflows/handson";
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const envPath = path.join(__dirname, "..", "..", ".env");
const envResult = dotenv.config({ path: envPath });

export const mastra = new Mastra({
  agents: { assistantAgent },
  workflows: { handsonWorkflow },
});
