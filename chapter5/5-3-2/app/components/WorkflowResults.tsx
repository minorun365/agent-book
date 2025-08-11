import { WorkflowResult } from "../types/workflow";

// WorkflowResultsコンポーネントのProps（引数）の型定義
interface WorkflowResultsProps {
  result: WorkflowResult | null;
}

export const WorkflowResults = ({result}: WorkflowResultsProps) => {
  if (!result) return null;

  // 実行中かどうかを判定
  const isRunning = result.message.includes("実行中");

  return (
    <div className="mt-8 border-t-2 border-gray-100 pt-8">
      <h2
        className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-6">
        📊 実行結果
      </h2>

      {/* 結果ステータス表示 */}
      <div className={`
       p-6 rounded-2xl mb-6 transition-all duration-300 shadow-lg
       ${isRunning
        ? "bg-gradient-to-r from-gray-50 to-gray-100 border-2 border-gray-300"
        : result.success
          ? "bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-300"
          : "bg-gradient-to-r from-red-50 to-pink-50 border-2 border-red-300"
      }
     `}>
        <div className="flex items-center">
          {/* ステータスアイコン */}
          {isRunning ? (
            <div className="mr-4">
              <svg className="animate-spin h-8 w-8 text-blue-600" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"
                        fill="none"/>
                <path className="opacity-75" fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
              </svg>
            </div>
          ) : result.success ? (
            <div className="text-3xl mr-4">🎉</div>
          ) : (
            <div className="text-3xl mr-4">🚨</div>
          )}
          <span className={`
           text-lg font-semibold
           ${isRunning
            ? "text-gray-800"
            : result.success
              ? "text-green-800"
              : "text-red-800"
          }
         `}>
           {result.message}
         </span>
        </div>

        {result.error && (
          <div className="mt-2 text-sm text-red-700">
            エラー詳細: {result.error}
          </div>
        )}
      </div>


      {/* Confluence検索結果 */}
      {result.confluencePages && result.confluencePages.length > 0 && (
        <div className="mb-8">
          <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
            <span className="text-2xl mr-2">📚</span> Confluenceページ
          </h3>
          <div className="grid gap-4">
            {result.confluencePages.map((page, index) => (
              <div key={index}
                   className="bg-white p-5 rounded-xl border-2 border-gray-200 hover:border-blue-300 hover:shadow-md transition-all duration-200">
                <div className="font-bold text-lg text-gray-900">{page.title}</div>
                {page.message && (
                  <div className="text-gray-600 mt-2">
                    {page.message}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
      {/* GitHub Issue結果 */}
      {result.githubIssues && result.githubIssues.length > 0 && (
        <div>
          <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
            <span className="text-2xl mr-2">🐙</span> GitHub Issues
          </h3>
          <div className="grid gap-4">
            {result.githubIssues.map((issue, index) => (
              <div key={index}
                   className="bg-gradient-to-r from-purple-50 to-pink-50 p-5 rounded-xl border-2 border-purple-200 hover:border-purple-400 hover:shadow-md transition-all duration-200">
                <div className="font-bold text-lg text-gray-900">{issue.title}</div>
                <div className="flex items-center justify-between mt-3">
                 <span className="text-purple-700 font-semibold text-lg">
                   #{issue.issueNumber}
                 </span>
                  {issue.issueUrl && (
                    <a
                      href={issue.issueUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-colors"
                    >
                      Issueを開く
                      <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                              d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
                      </svg>
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
