import { NextRequest, NextResponse } from "next/server";


export async function POST(request: NextRequest) {
    try {
        // リクエストボディを取得
        const body = await request.json();
        const { query, owner, repo } = body;


        // バリデーションを実施（パラメーターが不足していたらエラーを返す）
        if (!query || !owner || !repo) {
            return NextResponse.json(
                { error: '必要なパラメータが不足しています' },
                { status: 400 }
            );
        }
        // Mastraワークフローインスタンスを取得
        const { mastra } = await import('@/src/mastra');
        const workflow = mastra.getWorkflow('handsonWorkflow');

        if (!workflow) {
            throw new Error('ワークフローが見つかりません');
        }


        // ワークフローを実行
        const run = workflow.createRun();
        const result = await run.start({
            inputData: { query, owner, repo }
        });
// Mastraワークフローの結果から必要な情報を抽出
        const workflowOutput = result.status === 'success' ? result.result : null;
        const createdIssues = workflowOutput?.createdIssues || [];


        // 結果をAPIレスポンスとして返却
        return NextResponse.json({
            success: result.status === 'success',
            confluencePages: [{
                title: query,
                message: "要件書の検索と取得が完了しました"
            }],
            githubIssues: createdIssues,
            message: 'ワークフローが正常に完了しました',
            steps: result.steps ? Object.keys(result.steps).map(stepId => ({
                stepId,
                status: (result.steps as any)[stepId].status
            })) : []
        });


    } catch (error) {
        // エラーをAPIレスポンスとして返却
        return NextResponse.json(
            {
                error: 'ワークフローの実行中にエラーが発生しました',
                details: error instanceof Error ? error.message : 'エラー'
            },
            { status: 500 }
        );
    }
}
