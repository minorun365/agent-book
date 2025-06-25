import { createWorkflow, createStep } from "@mastra/core/workflows";
import {
  confluenceSearchPagesTool,
  confluenceGetPageTool,
} from "../tools/confluenceTool";
import { githubCreateIssueTool } from "../tools/githubTool";
import { assistantAgent } from "../agents/assistantAgent";
import { z } from "zod";

const confluenceSearchPagesStep = createStep(confluenceSearchPagesTool);
const confluenceGetPageStep = createStep(confluenceGetPageTool);
const githubCreateIssueStep = createStep(githubCreateIssueTool);

export const handsonWorkflow = createWorkflow({
  id: "handsonWorkflow",
  description:
    "自然言語の質問からConfluenceで要件書を検索し、GitHub Issueとして開発バックログを自動作成します。",
  inputSchema: z.object({
    query: z
      .string()
      .describe(
        "検索したい内容を自然言語で入力してください（例：「AIについての情報」「最新のプロジェクト情報」）"
      ),
    owner: z
      .string()
      .describe("GitHubリポジトリの所有者名（ユーザー名またはorganization名）"),
    repo: z.string().describe("GitHubリポジトリ名"),
  }),
  outputSchema: githubCreateIssueTool.outputSchema,
})
  .then(
    createStep({
      id: "generate-cql-query",
      inputSchema: z.object({
        query: z.string(),
        owner: z.string(),
        repo: z.string(),
      }),
      outputSchema: z.object({ cql: z.string() }),
      execute: async ({ inputData }) => {
        const prompt = `
以下の自然言語の検索要求をConfluence CQL (Confluence Query Language)に変換してください。
CQLの基本的な構文：
- text ~ "検索語"：全文検索
- title ~ "タイトル"：タイトル検索
- space = "スペースキー"：特定のスペース内検索
- type = page：ページのみ検索
- created >= "2024-01-01"：日付フィルタ

検索要求: ${inputData.query}

重要：
- 単純な単語検索の場合は、text ~ "単語" の形式を使用
- 複数の単語を含む場合は AND で結合
- 日本語の検索語もそのまま使用可能
- レスポンスはCQLクエリのみを返してください

CQLクエリ:`;

        try {
          const result = await assistantAgent.generate(prompt);
          const cql = result.text.trim();
          return { cql };
        } catch (error) {
          const fallbackCql = `text ~ "${inputData.query}"`;
          return { cql: fallbackCql };
        }
      },
    })
  )
  .then(confluenceSearchPagesStep)
  .then(
    createStep({
      id: "select-first-page",
      inputSchema: z.object({
        pages: z.array(
          z.object({
            id: z.string(),
            title: z.string(),
            url: z.string().optional(),
          })
        ),
        total: z.number(),
        error: z.string().optional(),
      }),
      outputSchema: z.object({
        pageId: z.string(),
        expand: z.string().optional(),
      }),
      execute: async ({ inputData }) => {
        const { pages, error } = inputData;

        if (error) {
          throw new Error(`検索エラー: ${error}`);
        }

        if (!pages || pages.length === 0) {
          throw new Error("検索結果が見つかりませんでした。");
        }

        // 最初のページを取得
        const firstPage = pages[0];
        return {
          pageId: firstPage.id,
          expand: "body.storage",
        };
      },
    })
  )
  .then(confluenceGetPageStep)
  .then(
    createStep({
      id: "create-development-tasks",
      inputSchema: confluenceGetPageTool.outputSchema,
      outputSchema: githubCreateIssueTool.inputSchema,
      execute: async ({ inputData, getInitData }) => {
        const { page, error } = inputData;
        const { owner, repo, query } = getInitData();

        if (error || !page || !page.content) {
          return {
            owner: owner || "",
            repo: repo || "",
            issues: [
              {
                title: "エラー: ページの内容が取得できませんでした",
                body: "Confluenceページの内容を取得できませんでした。",
              },
            ],
          };
        }

        const analysisPrompt = `以下のConfluenceページの内容は要件書です。この要件書を分析して、開発バックログのGitHub Issueを複数作成するための情報を生成してください。
 
 
 ユーザーの質問: ${query}
 
 
 ページタイトル: ${page.title}
 ページ内容:
 ${page.content}
 
 
 以下の形式でJSON配列形式で回答してください：
 [
  {
    "title": "機能1の実装",
    "body": "## 概要\\n機能1の詳細説明\\n\\n"
  },
  {
    "title": "機能2の実装",
    "body": "## 概要\\n機能2の詳細説明\\n\\n"
  }
 ]
 
 
 重要：
 - 要件書の内容を機能やコンポーネント単位で分割
 - 各Issueのタイトルは簡潔で分かりやすく
 - 本文はMarkdown形式で構造化
 - 2つIssueを作成
 - 曖昧な部分は「要確認」として記載`;

        try {
          const result = await assistantAgent.generate(analysisPrompt);

          try {
            const parsed = JSON.parse(result.text);
            const issues = Array.isArray(parsed) ? parsed : [parsed];
            return {
              owner,
              repo,
              issues: issues.map((issue) => ({
                title: issue.title || "要件書から生成された開発タスク",
                body: issue.body || "要件書の内容を確認してください。",
              })),
            };
          } catch (parseError) {
            // JSON解析に失敗した場合のフォールバック
            return {
              owner: owner,
              repo: repo,
              issues: [
                {
                  title: `要件書: ${query}`,
                  body: result.text,
                },
              ],
            };
          }
        } catch (error) {
          return {
            owner: owner,
            repo: repo,
            issues: [
              {
                title: "エラー: Issue作成に失敗",
                body: "エラーが発生しました: " + String(error),
              },
            ],
          };
        }
      },
    })
  )
  .then(githubCreateIssueStep)
  .commit();
