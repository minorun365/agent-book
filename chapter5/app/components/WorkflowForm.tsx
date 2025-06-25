"use client";

import { WorkflowFormData } from '../types/workflow';

interface WorkflowFormProps {
  formData: WorkflowFormData;
  isLoading: boolean;
  onInputChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onSubmit: (e: React.FormEvent) => void;
}

export const WorkflowForm = ({ 
  formData, 
  isLoading, 
  onInputChange, 
  onSubmit 
}: WorkflowFormProps) => {
  const isFormValid = formData.query && formData.owner && formData.repo;

  return (
      // フォームを定義
    <form onSubmit={onSubmit} className="space-y-6">
      {/*Confuence検索クエリ欄*/}
      <div>
        <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
          検索クエリ
        </label>
        <input
          type="text"
          id="query"
          name="query"
          value={formData.query}
          onChange={onInputChange}
          placeholder="例: AIについての情報"
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          required
        />
      </div>
      {/*GitHubアカウント名*/}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label htmlFor="owner" className="block text-sm font-medium text-gray-700 mb-2">
            GitHub Owner（ユーザー名/Organization）
          </label>
          <input
            type="text"
            id="owner"
            name="owner"
            value={formData.owner}
            onChange={onInputChange}
            placeholder="例: octocat"
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>
        {/*GitHubレポジトリ名*/}
        <div>
          <label htmlFor="repo" className="block text-sm font-medium text-gray-700 mb-2">
            GitHub Repository
          </label>
          <input
            type="text"
            id="repo"
            name="repo"
            value={formData.repo}
            onChange={onInputChange}
            placeholder="例: mastra_practice"
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>
      </div>

      {/* フォームの送信ボタン（ワークフローの実行ボタン） */}
      <div className="flex justify-end">
        <button
          type="submit"
          disabled={!isFormValid || isLoading}
          className={`
            px-6 py-3 rounded-md font-medium transition-colors
            ${isFormValid && !isLoading
              ? 'bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }
          `}
        >
          {isLoading ? (
            <div className="flex items-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              実行中...
            </div>
          ) : (
            'ワークフロー実行'
          )}
        </button>
      </div>
    </form>
  );
}