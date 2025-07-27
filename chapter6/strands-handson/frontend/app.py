import os, asyncio, boto3
import streamlit as st
from agent_executor import invoke_agent

# Streamlitシークレットを環境変数に設定
os.environ['AWS_ACCESS_KEY_ID'] = st.secrets["AWS_ACCESS_KEY_ID"]
os.environ['AWS_SECRET_ACCESS_KEY'] = st.secrets["AWS_SECRET_ACCESS_KEY"]
os.environ['AWS_DEFAULT_REGION'] = st.secrets["AWS_DEFAULT_REGION"]
os.environ['AGENT_RUNTIME_ARN'] = st.secrets["AGENT_RUNTIME_ARN"]

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
agent_core = boto3.client('bedrock-agentcore')

# ユーザー入力を表示
if prompt := st.chat_input("メッセージを入力してね"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # エージェントの応答を表示
    with st.chat_message("assistant"):
        container = st.container()
        try:
            final_response = asyncio.run(
                invoke_agent(prompt, container, agent_core)
            )
            if final_response:
                st.session_state.messages.append(
                    {"role": "assistant", "content": final_response}
                )
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
            st.error("AgentCore Runtimeの接続を確認してください。")