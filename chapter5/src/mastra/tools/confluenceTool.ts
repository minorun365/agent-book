// 必要なモジュールをインポート
import { createTool } from "@mastra/core/tools";
import { z } from "zod";

const CONFLUENCE_BASE_URL = process.env.CONFLUENCE_BASE_URL || "";
const CONFLUENCE_API_TOKEN = process.env.CONFLUENCE_API_TOKEN || "";
const CONFLUENCE_USER_EMAIL = process.env.CONFLUENCE_USER_EMAIL || "";

function getAuthHeaders(): Record<string, string> {
  const auth = Buffer.from(
    `${CONFLUENCE_USER_EMAIL}:${CONFLUENCE_API_TOKEN}`
  ).toString("base64");
  return {
    Authorization: `Basic ${auth}`,
    Accept: "application/json",
    "Content-Type": "application/json",
  };
}

async function callConfluenceAPI(
  endpoint: string,
  options: RequestInit = {}
): Promise<any> {
  const baseUrl = CONFLUENCE_BASE_URL.endsWith('/') 
    ? CONFLUENCE_BASE_URL.slice(0, -1) 
    : CONFLUENCE_BASE_URL;
  
  const url = `${baseUrl}/wiki/rest/api${endpoint}`;
  console.log("Headers:", {
    ...getAuthHeaders(),
    "Note": "Authorization header is shown above"
  });

  const response = await fetch(url, {
    ...options,
    headers: {
      ...getAuthHeaders(),
      ...options.headers,
    },
  });

  if (!response.ok) {
    const text = await response.text();
    console.error("API Error Response:", text);
    throw new Error(`Confluence API error: ${response.status} ${response.statusText}\nResponse: ${text}`);
  }

  const contentType = response.headers.get("content-type");
  if (contentType && contentType.includes("application/json")) {
    return response.json();
  } else {
    const text = await response.text();
    console.error("Non-JSON response:", text.substring(0, 200));
    throw new Error(`Expected JSON response but got ${contentType}`);
  }
}

// Confluenceページ検索ツール
export const confluenceSearchPagesTool = createTool({
  // ツールのID
  id: "confluence-search-pages",
  // ツールの説明
  description: "Confluenceでページを検索します（CQLクエリ対応）",
  // ツールの入力パラメーター
  inputSchema: z.object({
    cql: z.string().describe("CQL（Confluence Query Language）検索クエリ"),
  }),
  // ツールの出力パラメーター
  outputSchema: z.object({
    pages: z.array(
      z.object({
        id: z.string().describe("ページのID"),
        title: z.string().describe("ページのタイトル"),
        url: z.string().optional().describe("ページのURL"),
      })
    ),
    total: z.number().describe("検索結果の総数"),
    error: z.string().optional().describe("エラーメッセージ"),
  }),
  execute: async ({ context }) => {
    // CQLクエリをURLエンコードしてパラメータに追加
    const params = new URLSearchParams();
    params.append("cql", context.cql);

    try {
      // APIコール
      const data = await callConfluenceAPI(`/search?${params.toString()}`);

      const pages = data.results.map((result: any) => ({
        id: result.content?.id,
        title: result.content?.title,
        url: result.url ? `${CONFLUENCE_BASE_URL}/wiki${result.url}` : null,
      }));

      return { pages, total: data.totalSize };
    } catch (error) {
      return { pages: [], total: 0, error: String(error) };
    }
  },
});

// Confluenceページ詳細取得ツール
export const confluenceGetPageTool = createTool({
  id: "confluence_get_page",
  description: "指定されたIDのConfluenceページの詳細を取得します",
  inputSchema: z.object({
    pageId: z.string().describe("取得するページのID"),
    expand: z
      .string()
      .optional()
      .describe("追加で取得する情報（body.storage,version,space）"),
  }),
  outputSchema: z.object({
    page: z.object({
      id: z.string().describe("ページのID"),
      title: z.string().describe("ページのタイトル"),
      url: z.string().describe("ページのURL"),
      content: z.string().optional().describe("ページのコンテンツ（HTML形式）"),
    }),
    error: z.string().optional().describe("エラーメッセージ"),
  }),
  execute: async ({ context }) => {
    // 入力パラメータからページIDと展開オプションを取得
    const params = new URLSearchParams();
    if (context.expand) params.append("expand", context.expand);

    try {
      const endpoint = `/content/${context.pageId}${params.toString() ? `?${params.toString()}` : ""}`;
      // APIコール
      const page = await callConfluenceAPI(endpoint);

      return {
        page: {
          id: page.id,
          title: page.title,
          url: `${CONFLUENCE_BASE_URL}/wiki${page._links?.webui}`,
          content: page.body?.storage?.value || undefined,
        },
      };
    } catch (error) {
      return { 
        error: String(error),
        page: {
          id: '',
          title: '',
          url: '',
          content: undefined,
        }
      };
    }
  },
});
