import { createTool } from "@mastra/core/tools";
import { z } from "zod";

const token = process.env.GITHUB_TOKEN;

export const githubCreateIssueTool = createTool({
  id: "githubCreateIssue",
  description:
    "GitHub上で複数のイシューを作成します。バグ報告、機能要求、質問などに使用できます。",
  inputSchema: z.object({
    owner: z
      .string()
      .describe("リポジトリの所有者名（ユーザー名またはorganization名）"),
    repo: z.string().describe("リポジトリ名"),
    issues: z.array(z.object({
      title: z.string().describe("イシューのタイトル"),
      body: z.string().optional().describe("イシューの本文・詳細説明"),
    })).describe("作成するイシューのリスト"),
  }),
  outputSchema: z.object({
    success: z.boolean(),
    createdIssues: z.array(z.object({
      issueNumber: z.number().optional(),
      issueUrl: z.string().optional(),
      title: z.string(),
    })),
    errors: z.array(z.string()).optional(),
  }),
  execute: async ({ context }) => {
    const { owner, repo, issues } = context;
    
    const createdIssues = [];
    const errors = [];

    for (const issue of issues) {
      try {
        
        const response = await fetch(
          `https://api.github.com/repos/${owner}/${repo}/issues`,
          {
            method: "POST",
            headers: {
              Accept: "application/vnd.github+json",
              Authorization: `Bearer ${token}`,
              "X-GitHub-Api-Version": "2022-11-28",
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              title: issue.title,
              body: issue.body,
            }),
          }
        );

        if (!response.ok) {
          const errorData = await response.json();
          const errorMessage = `GitHub API エラー: ${response.status} - ${errorData.message || "Unknown error"}`;
          errors.push(`Failed to create issue "${issue.title}": ${errorMessage}`);
          continue;
        }

        const issueData = await response.json();
        
        createdIssues.push({
          issueNumber: issueData.number,
          issueUrl: issueData.html_url,
          title: issue.title,
        });
      } catch (error) {
        const errorMessage = `リクエスト失敗: ${error instanceof Error ? error.message : "Unknown error"}`;
        console.error(`Error creating issue "${issue.title}":`, errorMessage);
        errors.push(`Error creating issue "${issue.title}": ${errorMessage}`);
      }
    }

    return {
      success: createdIssues.length > 0,
      createdIssues,
      errors: errors.length > 0 ? errors : undefined,
    };
  },
});
