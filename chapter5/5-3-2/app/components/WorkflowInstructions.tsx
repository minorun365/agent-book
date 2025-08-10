export const WorkflowInstructions = () => {
  return (
    <div
      className="bg-gradient-to-br from-blue-50 to-purple-50
       border-2 border-blue-200 rounded-2xl p-6 shadow-md
       hover:shadow-lg transition-shadow">
      <h3 className="text-xl font-bold text-transparent
       bg-gradient-to-r from-blue-700 to-purple-700
        bg-clip-text mb-4">
        ✨ ワークフローの流れ
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2
       lg:grid-cols-4 gap-4">
        <div className="flex items-start space-x-3">
          <span
            className="flex-shrink-0 w-8 h-8 bg-blue-600
             text-white rounded-full flex items-center
              justify-center font-bold">1</span>
          <p className="text-gray-700 font-medium">Confluenceの要件定義を検索</p>
        </div>
        <div className="flex items-start space-x-3">
          <span
            className="flex-shrink-0 w-8 h-8 bg-purple-600
             text-white rounded-full flex items-center
              justify-center font-bold">2</span>
          <p className="text-gray-700 font-medium">要件定義を分析</p>
        </div>
        <div className="flex items-start space-x-3">
          <span
            className="flex-shrink-0 w-8 h-8 bg-indigo-600
             text-white rounded-full flex items-center
              justify-center font-bold">3</span>
          <p className="text-gray-700 font-medium">バックログに分解</p>
        </div>
        <div className="flex items-start space-x-3">
          <span
            className="flex-shrink-0 w-8 h-8 bg-pink-600
             text-white rounded-full flex items-center
              justify-center font-bold">4</span>
          <p className="text-gray-700 font-medium">GitHub Issue作成</p>
        </div>
      </div>
    </div>
  );
}
