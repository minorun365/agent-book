import { createWorkflow, createStep } from "@mastra/core/workflows";
import { confluenceSearchPagesTool, confluenceGetPageTool } from "../tools/confluenceTool";
import { assistantAgent } from "../agents/assistantAgent";
import { z } from "zod";

// ツールからステップを作成
const confluenceSearchPagesStep = createStep(confluenceSearchPagesTool);
const confluenceGetPageStep = createStep(confluenceGetPageTool);
export const handsonWorkflow = createWorkflow({
  id: "handsonWorkflow",
  description:
    "自然言語の質問からConfluenceで要件書を検索し、内容を要約して回答します。",
  inputSchema: z.object({
    query: z
      .string()
      .describe(
        "検索したい内容を自然言語で入力してください（例：「AIについての情報」「最新のプロジェクト情報」）"
      ),
  }),
  outputSchema: z.object({
    text: z.string().describe("要約された回答"),
  }),
})
  .then(
    createStep({
      id: "generate-cql-query",
      inputSchema: z.object({
        query: z.string(),
      }),
      outputSchema: z.object({cql: z.string()}),
      execute: async ({inputData}) => {
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
          return {cql};
        } catch (error) {
          const fallbackCql = `text ~ "${inputData.query}"`;
          return {cql: fallbackCql};
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
      execute: async ({inputData}) => {
        // ページの一覧取得
        const {pages, error} = inputData;
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
  // Confluenceページを取得するステップを追加
  .then(confluenceGetPageStep)
  .then(
    createStep({
      id: "prepare-prompt",
      inputSchema: z.object({
        page: z.object({
          id: z.string(),
          title: z.string(),
          url: z.string(),
          content: z.string().optional(),
        }),
        error: z.string().optional(),
      }),
      outputSchema: z.object({
        prompt: z.string(),
        originalQuery: z.string(),
        pageTitle: z.string(),
        pageUrl: z.string(),
      }),
      execute: async ({inputData, getInitData}) => {
        // 一つ前のステップのoutpuSchemaから渡されたデータ
        const {page, error} = inputData;
        // ワークフローの最初に設定されたデータ
        const initData = getInitData();

        if (error || !page || !page.content) {
          return {
            prompt: "ページの内容が取得できませんでした。",
            originalQuery: initData.query || "",
            pageTitle: page?.title || "不明",
            pageUrl: page?.url || "",
          };
        }
        // エージェントへの指示を作成
        const prompt = `以下のConfluenceページの内容に基づいて、ユーザーの質問に答えてください。

ユーザーの質問: ${initData.query}

ページタイトル: ${page.title}
ページ内容:
${page.content}

回答は簡潔で分かりやすく、必要に応じて箇条書きを使用してください。`;
        return {
          prompt,
          originalQuery: initData.query || "",
          pageTitle: page.title,
          pageUrl: page.url,
        };
      },
    })
  )
  .then(
    createStep({
      id: "assistant-response",
      inputSchema: z.object({
        prompt: z.string(),
        originalQuery: z.string(),
        pageTitle: z.string(),
        pageUrl: z.string(),
      }),
      // ワークフローのoutputSchemaと一致させる
      outputSchema: z.object({text: z.string(),}),
      execute: async ({inputData}) => {
        try {
          // エージェントを実行しテキスト生成結果を受け取る
          const result = await assistantAgent.generate(inputData.prompt);
          return {
            text: result.text,
          };
        } catch (error) {
          return {text: "エラーが発生しました: " + String(error),};
        }
      },
    })
  )
  .commit();