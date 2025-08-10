"use client";

import { useState } from 'react';
import { WorkflowForm } from './components/WorkflowForm';
import { WorkflowInstructions } from './components/WorkflowInstructions';
import { WorkflowResults } from './components/WorkflowResults';
import { WorkflowFormData, WorkflowResult } from './types/workflow';


// ワークフローのメインページコンポーネント
const Page = () => {
  // フォームの状態を管理するためのuseStateフック
  const [formData, setFormData] = useState<WorkflowFormData>({
    query: "",
    owner: "",
    repo: ""
  });
  // ワークフローの実行状態と結果を管理するためのuseStateフック
  const [isLoading, setIsLoading] = useState(false);
  // ワークフローの結果を管理するためのuseStateフック
  const [result, setResult] = useState<WorkflowResult | null>(null);
  // 入力フィールドの変更を処理する関数
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // 入力フィールドの名前と値を取得
    const { name, value } = e.target;
    // フォームデータの状態を更新
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // フォームの送信を処理する関数
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // フォームが送信されたときにローディング状態を設定し、結果を初期化
    setIsLoading(true);
    // ワークフローの結果を初期化
    setResult({
      success: false,
      message: "ワークフローを実行中...",
      confluencePages: [],
      githubIssues: [],
      steps: []
    });

    try {
      // APIエンドポイントにPOSTリクエストを送信
      const response = await fetch("/api/workflow/execute", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // 結果をJSON形式で取得
      const data = await response.json();
      // レスポンスの結果をstateに設定
      setResult(data);
    } catch (error) {
      setResult({
        success: false,
        message: "ワークフローの実行中にエラーが発生しました",
        error: error instanceof Error ? error.message : "不明なエラー",
        confluencePages: [],
        githubIssues: [],
        steps: []
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br
     from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white/90 backdrop-blur-sm
           rounded-2xl shadow-xl border border-gray-100
            p-8 transition-all hover:shadow-2xl">
            <h1 className="text-3xl font-bold
             bg-gradient-to-r from-blue-600
              to-purple-600 bg-clip-text
               text-transparent mb-8">
              要件書→プロダクトバックログ ワークフロー
            </h1>

            {/* ワークフローの説明と手順を表示するコンポーネント */}
            <div className="mb-8">
              <WorkflowInstructions />
            </div>

            {/* ワークフローのフォームコンポーネント */}
            <WorkflowForm
              formData={formData}
              isLoading={isLoading}
              onInputChange={handleInputChange}
              onSubmit={handleSubmit}
            />

            {/* ワークフローの結果を表示するコンポーネント */}
            <WorkflowResults result={result} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Page;