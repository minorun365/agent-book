import { cookies } from "next/headers";
import { createServerRunner } from "@aws-amplify/adapter-nextjs";
import { fetchAuthSession } from "aws-amplify/auth/server";
// Amplifyの設定ファイルをインポート
import outputs from "../amplify_outputs.json";

// Amplifyのサーバーランナーを作成
const serverRunner = createServerRunner({
  config: outputs,
});

export const { runWithAmplifyServerContext } = serverRunner;

// サーバーサイドで認証セッションを取得する関数
export async function AuthFetchAuthSessionServer() {
  try {
    const session = await runWithAmplifyServerContext({
      nextServerContext: { cookies },
      operation: (contextSpec: any) => fetchAuthSession(contextSpec),
    });
    return session;
  } catch (error) {
    return null;
  }
}