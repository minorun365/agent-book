import { WorkflowResult } from '../types/workflow';

interface WorkflowResultsProps {
  result: WorkflowResult | null;
}

export const WorkflowResults = ({ result }: WorkflowResultsProps) => {
  if (!result) return null;

  // 実行中かどうかを判定
  const isRunning = result.message.includes('実行中');

  return (
    <div className="mt-8 border-t pt-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">実行結果</h2>
      
      {/* 結果ステータス表示 */}
      <div className={`
        p-4 rounded-lg mb-4
        ${isRunning 
          ? 'bg-gray-50 border border-gray-200' 
          : result.success 
            ? 'bg-green-50 border border-green-200' 
            : 'bg-red-50 border border-red-200'
        }
      `}>
        <div className="flex items-center">
          {/* ステータスアイコン */}
          {isRunning ? (
            <div className="text-gray-600 mr-3 animate-spin">⚙️</div>
          ) : result.success ? (
            <div className="text-green-600 mr-3">✅</div>
          ) : (
            <div className="text-red-600 mr-3">❌</div>
          )}
          <span className={`
            font-medium
            ${isRunning 
              ? 'text-gray-800' 
              : result.success 
                ? 'text-green-800' 
                : 'text-red-800'
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

      {/* Confluenceページ結果 */}
      {result.confluencePages && result.confluencePages.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-medium text-gray-900 mb-3">
            検索されたConfluenceページ
          </h3>
          <div className="space-y-2">
            {/* resultのconfluencePagesを.mapでループして表示 */}
            {result.confluencePages.map((page, index) => (
              <div key={index} className="bg-gray-50 p-3 rounded border">
                <div className="font-medium text-gray-900">{page.title}</div>
                {page.message && (
                  <div className="text-sm text-gray-600 mt-1">
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
          <h3 className="text-lg font-medium text-gray-900 mb-3">
            作成されたGitHub Issues
          </h3>
          <div className="space-y-2">
            {/* resultのgithubIssuesを.mapでループして表示 */}
            {result.githubIssues.map((issue, index) => (
              <div key={index} className="bg-gray-50 p-3 rounded border">
                <div className="font-medium text-gray-900">{issue.title}</div>
                <div className="text-sm text-gray-600 mt-1">
                  #{issue.issueNumber}
                  { " " }
                  {issue.issueUrl && (
                  <a 
                    href={issue.issueUrl} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    Issueを開く →
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