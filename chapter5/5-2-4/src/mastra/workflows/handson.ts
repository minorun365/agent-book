import { createWorkflow, createStep } from "@mastra/core/workflows";
import {
  confluenceSearchPagesTool,
  confluenceGetPageTool,
} from "../tools/confluenceTool";
// 作成したツールをimport
import { githubCreateIssueTool } from "../tools/githubTool";
import { assistantAgent } from "../agents/assistantAgent";
import { z } from "zod";


const confluenceSearchPagesStep = createStep(confluenceSearchPagesTool);
const confluenceGetPageStep = createStep(confluenceGetPageTool);
// 作成したGitHub Issuesツールをステップ化
const githubCreateIssueStep = createStep(githubCreateIssueTool);
export const handsonWorkflow = createWorkflow({
  id: "handsonWorkflow",
// ワークフローの動作が変わったため修正
  description:
    "自然言語の質問からConfluenceで要件書を検索し、GitHub Issueとして開発バックログを自動作成します。",
  inputSchema: z.object({
    query: z
      .string()
      .describe(
        "検索したい内容を自然言語で入力してください（例：「AIについての情報」「最新のプロジェクト情報」）"
      ),
    // GitHubアカウント名を追加
    owner: z
      .string()
      .describe("GitHubリポジトリの所有者名（ユーザー名またはorganization名）"),
    // GitHubリポジトリ名を追加
    repo: z.string().describe("GitHubリポジトリ名"),
  }),
// GitHubツールのoutputSchemaをそのまま指定
  outputSchema: githubCreateIssueTool.outputSchema,
})
  .then(
    createStep({
      id: "generate-cql-query",
      inputSchema: z.object({
        // ワークフローのinputSchemaと合わせる
        query: z.string(), owner: z.string(), repo: z.string(),
      }),
      outputSchema: z.object({cql: z.string()}),
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
          const result = await assistantAgent.generateVNext(prompt);
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
        // ページの一覧取得
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
  // Confluenceページを取得するステップを追加
  .then(confluenceGetPageStep)
  .then(
    createStep({
      id: "create-development-tasks",
      // Confluenceページ作成ツールのoutputSchemaをそのまま指定
      inputSchema: confluenceGetPageTool.outputSchema,
      // GitHub Issues作成ツールのinputSchemaをそのまま指定
      outputSchema: githubCreateIssueTool.inputSchema,
      execute: async ({ inputData, getInitData }) => {
        // 前のステップから受け渡されるConfluenceのページ情報
        const { page, error } = inputData;
        // GitHubのリポジトリ情報はワークフローの初期データから取得
        const { owner, repo, query } = getInitData();


        // いずれかの情報が取れない場合はエラーメッセージを送信
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
        // エージェントからの出力フォーマットを規定
        const outputSchema = z.object({
          issues: z.array(
            z.object({
              title: z.string(),
              body: z.string(),
            })
          ),
        });
        // プロンプト
        const analysisPrompt = `以下のConfluenceページの内容は要件書です。この要件書を分析して、開発バックログのGitHub Issueを複数作成するための情報を生成してください。
ユーザーの質問: ${query}
ページタイトル: ${page.title}
ページ内容:
${page.content}
重要：
- 要件書の内容を機能やコンポーネント単位で分割
- 各Issueのtitleは簡潔で分かりやすく
- bodyはMarkdown形式で構造化
- フォーマットはJSON配列形式で、必ず出力。枕詞は不要。トップの配列は必ず角括弧で囲む。
- \`\`\`jsonのようなコードブロックは不要
- 2つIssueを作成
- 曖昧な部分は「要確認」として記載`;

        try {
          const result = await assistantAgent.generateVNext(analysisPrompt, {
            output: outputSchema, // エージェントからの出力フォーマットを指定
          });
          // JSONからIssueの配列を取り出す
          const parsedResult = JSON.parse(result.text);
          const issues = parsedResult.issues.map((issue: any) => ({
            title: issue.title,
            body: issue.body,
          }));
          return {
            owner: owner || "",
            repo: repo || "",
            issues: issues,
          };
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