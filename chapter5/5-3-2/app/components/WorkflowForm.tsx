"use client";

import {WorkflowFormData} from '../types/workflow';

// WorkflowFormコンポーネントのProps（引数）の型定義
interface WorkflowFormProps {
  formData: WorkflowFormData;
  isLoading: boolean;
  onInputChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onSubmit: (e: React.FormEvent) => void;
}

// WorkflowフォームのUIコンポーネント
export const WorkflowForm = ({
                               formData,
                               isLoading,
                               onInputChange,
                               onSubmit
                             }: WorkflowFormProps) => {
  // 入力項目に不足がないかチェック
  const isFormValid = formData.query && formData.owner && formData.repo;
  return (
    // フォームを定義
    <form onSubmit={onSubmit} className="space-y-6">
      {/*Confuence検索クエリ欄*/}
      <div className="group">
        <label htmlFor="query"
               className="block text-sm font-semibold text-gray-700 mb-2 transition-colors group-hover:text-blue-600">
          🔍 検索クエリ
        </label>
        <input
          type="text"
          id="query"
          name="query"
          value={formData.query}
          onChange={onInputChange}
          placeholder="例: AIについての情報"
          className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl shadow-sm transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-blue-100 focus:border-blue-500 hover:border-gray-300"
          required
        />
      </div>
      {/*GitHubアカウント名*/}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="group">
          <label htmlFor="owner"
                 className="block text-sm font-semibold text-gray-700 mb-2 transition-colors group-hover:text-blue-600">
            👤 GitHub Owner
          </label>
          <input
            type="text"
            id="owner"
            name="owner"
            value={formData.owner}
            onChange={onInputChange}
            placeholder="例: octocat"
            className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl shadow-sm transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-blue-100 focus:border-blue-500 hover:border-gray-300"
            required
          />
        </div>
        {/*GitHubリポジトリ名*/}
        <div className="group">
          <label htmlFor="repo"
                 className="block text-sm font-semibold text-gray-700 mb-2 transition-colors group-hover:text-blue-600">
            📁 Repository
          </label>
          <input
            type="text"
            id="repo"
            name="repo"
            value={formData.repo}
            onChange={onInputChange}
            placeholder="例: mastra_practice"
            className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl shadow-sm transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-blue-100 focus:border-blue-500 hover:border-gray-300"
            required
          />
        </div>
      </div>
      {/* フォームの送信ボタン（ワークフローの実行ボタン） */}
      <div className="flex justify-end pt-4">
        <button
          type="submit"
          disabled={!isFormValid || isLoading}
          className={`
           px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-300 transform
           ${isFormValid && !isLoading
            ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 hover:scale-105 hover:shadow-lg focus:outline-none focus:ring-4 focus:ring-blue-300'
            : 'bg-gray-200 text-gray-400 cursor-not-allowed'
          }
         `}
        >
          {isLoading ? (
            <div className="flex items-center">
              <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"
                        fill="none"/>
                <path className="opacity-75" fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
              </svg>
              処理中...
            </div>
          ) : (
            <span className="flex items-center">
             ワークフロー実行 ✨
           </span>
          )}
        </button>
      </div>
    </form>
  );
}
