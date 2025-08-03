import os, asyncio, boto3
import streamlit as st
from dotenv import load_dotenv
from agent_executor import invoke

load_dotenv(override=True)

# タイトル表示
st.title("AWS開発お助けエージェント")
st.write("AWSドキュメントや、あなたのアカウントの調査をお手伝いします！")

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
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )
    
    # エージェントの応答を表示
    with st.chat_message("assistant"):
        container = st.container()
        try:
            response = asyncio.run(
                invoke(prompt, container, agent_core)
            )
            if response:
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")