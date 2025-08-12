import { NextRequest, NextResponse } from "next/server";


export async function POST(request: NextRequest) {
  try {
    // リクエストボディを取得
    const body = await request.json();
    const { query, owner, repo } = body;


    // バリデーションを実施（パラメーターが不足していたらエラーを返す）
    if (!query || !owner || !repo) {
      return NextResponse.json(
        { error: "必要なパラメータが不足しています" },
        { status: 400 }
      );
    }
    // Mastraワークフローインスタンスを取得
    const { mastra } = await import("@/src/mastra");
    const workflow = mastra.getWorkflow("handsonWorkflow");

    if (!workflow) {
      throw new Error("ワークフローが見つかりません");
    }

    // ワークフローを実行
    const run = await workflow.createRunAsync();
    const result = await run.start({
      inputData: { query, owner, repo }
    });

    // 返却メッセージとステータスを作成
    let message;
    let isSuccess;
    if (result.status === "success" && result.result.success) {
      message = "ワークフローが正常に完了しました";
      isSuccess = true;
    } else {
      message = `${(result as any).error} ${(result as any).result.errors}`;
      isSuccess = false;
    }
// Mastraワークフローの結果から必要な情報を抽出
    const workflowOutput = result.status === "success" ? result.result : null;
    const createdIssues = workflowOutput?.createdIssues || [];

    // 結果をAPIレスポンスとして返却
    return NextResponse.json({
      success: isSuccess,
      confluencePages: [{
        title: query,
        message: "要件書の検索と取得を実行しました"
      }],
      githubIssues: createdIssues,
      message: message,
      steps: result.steps ? Object.keys(result.steps).map(stepId => ({
        stepId,
        status: (result.steps as any)[stepId].status
      })) : []
    });

  } catch (error) {
    // エラーをAPIレスポンスとして返却
    return NextResponse.json(
      {
        error: "ワークフローの実行中にエラーが発生しました",
        details: error instanceof Error ? error.message : "エラー"
      },
      { status: 500 }
    );
  }
}