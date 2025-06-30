"use client";

import { useAuthenticator } from '@aws-amplify/ui-react';

export const Navigation = () => {
  const { user, signOut } = useAuthenticator((context) => [context.user]);

  return (
    <nav className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* タイトルを表示する部分 */}
          <div className="flex items-center space-x-8">
            <div className="flex-shrink-0">
              <h1 className="text-xl font-bold">AI Assistant</h1>
            </div>
          </div>
          {/* ユーザー情報とログアウトボタンを表示する部分 */}
          <div className="flex items-center space-x-4">
            { /* ユーザー名を表示する部分 */ }
            <span className="text-sm text-gray-600">
              {user?.signInDetails?.loginId}
            </span>
            { /* ログアウトボタン */ }
            <button
              onClick={signOut}
              className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
            >
              ログアウト
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}