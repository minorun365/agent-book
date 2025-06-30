import { AuthFetchAuthSessionServer } from "./amplify-server-utils";

export async function getBedrockModel() {
  try {
    // Amazon Bedrockのクライアントをインポート
    const { createAmazonBedrock } = await import("@ai-sdk/amazon-bedrock");
    // BedrockモデルのIDとリージョンを設定
    const modelId = "us.anthropic.claude-3-5-sonnet-20241022-v2:0";
    const region = process.env.AWS_REGION || "us-west-2";
    // 認証セッションを取得
    const session = await AuthFetchAuthSessionServer();
    if (!session || !session.credentials) {
      throw new Error("Failed to get authentication session");
    }
    // Amazon Bedrockのクライアントを作成
    const bedrock = createAmazonBedrock({
      region,
      accessKeyId: session.credentials.accessKeyId,
      secretAccessKey: session.credentials.secretAccessKey,
      sessionToken: session.credentials.sessionToken,
    });
    // モデルを取得
    const model = bedrock(modelId);
    return model;
  } catch (error) {
    throw error;
  }
}
