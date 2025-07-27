import asyncio, boto3
import streamlit as st
from dotenv import load_dotenv
from agent_executor import invoke_agent

load_dotenv()
agent_core = boto3.client('bedrock-agentcore')

# セッションを初期化
if 'messages' not in st.session_state:
    st.session_state.messages = []

# UI表示
st.title("AWSアカウント調査くん")
st.write("あなたのAWSアカウント操作をAPIで代行するよ！")

# メッセージ履歴を表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

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