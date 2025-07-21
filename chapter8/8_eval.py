
from langchain.chat_models import init_chat_model
from langfuse import get_client
from ragas.metrics import AgentGoalAccuracyWithReference, ToolCallAccuracy
from ragas.dataset_schema import  MultiTurnSample
from ragas.llms import LangchainLLMWrapper
from ragas.messages import AIMessage, HumanMessage, ToolMessage, ToolCall
from typing import Union
from datetime import datetime

# 環境変数の読み込み
from dotenv import load_dotenv
load_dotenv("../.env")

langfuse = get_client()

# 最新トレースデータを1件取得
def get_latest_trace():
    traces_batch = langfuse.api.trace.list(
        page=1,
        limit=1,
        order_by="timestamp.desc"
    ).data      
    trace = traces_batch[0]
    return trace

# LangfuseのトレースデータをRagasメッセージ形式に変換
def convert_trace_to_ragas_messages(trace):
    ragas_messages: Union[HumanMessage, AIMessage, ToolMessage] = []
    for message in trace.output["messages"]:
        if message["type"] == "ai": # AIMessage
            content_text = ""
            # ツール要求情報の取得
            tool_calls = [
                ToolCall(
                    name=tool_call["name"],
                    args=tool_call["args"]
                )
                for tool_call in message["tool_calls"]
            ]
            if isinstance(message["content"], list):    
                for content in message["content"]:
                    if content["type"] == "text":
                        content_text += content["text"]
            else:
                content_text=message["content"]
            ai_message = AIMessage(content=content_text, tool_calls=tool_calls)
            ragas_messages.append(ai_message)
        elif message["type"] == "human": # HumanMessage
            human_message = HumanMessage(content=message["content"])
            ragas_messages.append(human_message)
        elif message["type"] == "tool": # ToolMessage
            tool_message = ToolMessage(content=message["content"])
            ragas_messages.append(tool_message)
    return ragas_messages

# 評価の実施
def evaluate(messages):
    
    # 期待するツールの利用順序
    reference_tool_calls=[
        ToolCall(name="read_file", args={"file_path": "task.txt"}),
        ToolCall(name="tavily_search", args={"query": "横浜市西区みなとみらい 郵便番号"}),
        ToolCall(name="write_file", args={"file_path": "zip_code.txt", "text": "220-0012"}),
    ]
    # 期待する最終出力
    reference_goal  = "横浜市西区みなとみらいの郵便番号をファイル名「zip_code.txt」で保存しました。"

    # RagasのMultiTurnSampleの生成
    sample = MultiTurnSample(
        user_input=messages,
        reference=reference_goal,
        reference_tool_calls=reference_tool_calls
    )

    # LLMインスタンスの生成
    llm = init_chat_model(
        model="us.anthropic.claude-sonnet-4-20250514-v1:0",
        model_provider="bedrock_converse"
    )

    # 評価者の定義
    goal_evaluator = AgentGoalAccuracyWithReference(llm=LangchainLLMWrapper(llm))
    tool_call_evaluator = ToolCallAccuracy()
    
    # 評価の実行
    print("評価を実行中...")
    goal_score = goal_evaluator.multi_turn_score(sample)
    tool_call_score = tool_call_evaluator.multi_turn_score(sample)
    
    print(f"Goal Accuracy Score: {goal_score}")
    print(f"Tool Call Accuracy Score: {tool_call_score}")
    
    print("評価が完了しました")
    return trace.id, goal_score, tool_call_score

# 評価結果をLangfuseにアップロード
def upload_score(trace_id: str, goal_score: float, tool_call_score: float):
    # 評価メタデータをトレースに追加
    evaluation_metadata = {
        "evaluation_timestamp": datetime.now().isoformat(),
        "evaluation_method": "ragas",
    }
    # 評価結果をスコアとして記録
    langfuse.create_score(
        trace_id=trace_id,
        name="goal_accuracy",
        value=goal_score,
        metadata=evaluation_metadata
    )
    langfuse.create_score(
        trace_id=trace_id,
        name="tool_call_accuracy", 
        value=tool_call_score,
        metadata=evaluation_metadata
    )
    print("アップロードが完了しました")

if __name__ == "__main__":
    # 最新トレースの取得
    trace = get_latest_trace()
    # トレースからメッセージを抽出してRagas形式に変換
    ragas_messages = convert_trace_to_ragas_messages(trace)
    # 評価の実施
    trace_id, goal_score, tool_call_score = evaluate(ragas_messages)
    # 評価結果をLangfuseのトレースに記録
    upload_score(trace_id, goal_score, tool_call_score)

