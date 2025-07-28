import os, asyncio, boto3
import streamlit as st
from agent_executor import invoke_agent

# Streamlitシークレットを環境変数に設定
keys = [
    "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", 
    "AWS_DEFAULT_REGION", "AGENT_RUNTIME_ARN"
]
for key in keys:
    os.environ[key] = st.secrets[key]

# タイトル表示
st.title("AWSアカウント調査くん")
st.write("あなたのAWSアカウント操作をAPIで代行するよ！")

# セッションを初期化
if 'messages' not in st.session_state:
    st.session_state.messages = []

# メッセージ履歴を表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# AgentCore APIクライアントを初期化
core = boto3.client('bedrock-agentcore')

# ユーザー入力を表示
if prompt := st.chat_input("メッセージを入力してね"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )
    
    # エージェントの応答を表示
    with st.chat_message("assistant"):
        container = st.container()
        try:
            final_response = asyncio.run(
                invoke_agent(prompt, container, core)
            )
            if final_response:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": final_response
                })
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")