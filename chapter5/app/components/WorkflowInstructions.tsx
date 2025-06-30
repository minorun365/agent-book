export const WorkflowInstructions = () => {
  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <h3 className="text-lg font-medium text-blue-900 mb-2">
        ワークフローの流れ
      </h3>
      <ol className="list-decimal list-inside text-blue-800 space-y-1">
        <li>自然言語でConfluenceの要件書を検索</li>
        <li>見つかった要件書の内容を分析</li>
        <li>要件をプロダクトバックログアイテムに分解</li>
        <li>GitHub Issueとして自動作成</li>
      </ol>
    </div>
  );
}