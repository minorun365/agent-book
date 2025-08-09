import uuid
import streamlit as st
from langchain_core.messages import HumanMessage
from langgraph.types import Command

# core.pyからエージェントをインポート
from x_agent_core import agent

def init_session_state():
    """セッション状態を初期化する"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'waiting_for_approval' not in st.session_state:
        st.session_state.waiting_for_approval = False
    if 'final_result' not in st.session_state:
        st.session_state.final_result = None
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None

def reset_session():
    """セッション状態をリセットする"""
    st.session_state.messages = []
    st.session_state.waiting_for_approval = False
    st.session_state.final_result = None
    st.session_state.thread_id = None

# セッション状態の初期化を実行
init_session_state()

def run_agent(input_data):
    """エージェントを実行し、結果を処理する"""
    # AIエージェント呼び出しに使うconfigurationの作成
    config = {"configurable": 
        {"thread_id": st.session_state.thread_id}
    }
        
    # 結果を処理
    with st.spinner("処理中...", show_time=True):
        for chunk in agent.stream(input_data, stream_mode="updates", config=config):
            for task_name, result in chunk.items():
                # interruptの場合
                if task_name == "__interrupt__":
                    st.session_state.tool_info = result[0].value
                    st.session_state.waiting_for_approval = True
                # 最終回答の場合
                elif task_name == "agent":
                    st.session_state.final_result = result.content
                # LLM推論の場合
                elif task_name == "invoke_llm":
                    if isinstance(chunk["invoke_llm"].content, list):
                        for content in result.content:
                            if content["type"] == "text":
                                st.session_state.messages.append({"role": "assistant", "content": content["text"]})
                # ツール実行の場合
                elif task_name == "use_tool":
                    st.session_state.messages.append({"role": "assistant", "content": "ツールを実行！"})                            
        st.rerun()                

def feedback():
    """フィードバックを取得し、エージェントに通知する関数"""       
    approve_column, deny_column = st.columns(2)

    feedback_result = None
    with approve_column:
        if st.button("APPROVE", width="stretch"):
            st.session_state.waiting_for_approval = False
            feedback_result = "APPROVE"
    with deny_column:
        if st.button("DENY", width="stretch"):
            st.session_state.waiting_for_approval = False
            feedback_result = "DENY"
                
    # いずれかのボタンが押された場合
    return feedback_result

def app():
    # タイトルの設定
    st.title("Webリサーチエージェント")

    # メッセージ表示エリア
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])
            
    # ツール承認の確認
    if st.session_state.waiting_for_approval \
       and st.session_state.tool_info:
        st.info(st.session_state.tool_info["args"])
        if st.session_state.tool_info["name"] == "write_file":
            with st.container(height=400):
                st.html(st.session_state.tool_info["html"], width="stretch")
        feedback_result = feedback()
        if feedback_result:
            st.chat_message("user").write(feedback_result)
            st.session_state.messages.append({"role": "user", "content": feedback_result})
            run_agent(Command(resume=feedback_result))
            st.rerun()

    # 最終結果の表示
    if st.session_state.final_result \
       and not st.session_state.waiting_for_approval:
        st.subheader("最終結果")
        st.success(st.session_state.final_result)

    # ユーザー入力エリア
    if not st.session_state.waiting_for_approval:
        user_input = st.chat_input("メッセージを入力してください")
        if user_input:
            reset_session()
            # スレッドIDを設定
            st.session_state.thread_id = str(uuid.uuid4())
            # ユーザーメッセージを追加
            st.chat_message("user").write(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # エージェントを実行
            messages = [HumanMessage(content=user_input)]
            if run_agent(messages):
                st.rerun()
    else:
        st.info("ツールの承認待ちです。上記のボタンで応答してください。")

# メインの実行
if __name__ == "__main__":
    app()
