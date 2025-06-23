from crewai import Agent, Task, Crew

# エージェントの定義
researcher = Agent(
    role="リサーチャー",
    goal="トピックについて情報を収集する",
    backstory="あなたは情報収集のエキスパートです。"
)

# タスクの定義
research_task = Task(
    description="AIエージェントの最新トレンドについて調査してください",
    agent=researcher,
    expected_output="AIエージェントの最新トレンドまとめ"
)

# クルーの定義
crew = Crew(
    agents=[researcher],
    tasks=[research_task]
)

# クルーの実行
result = crew.kickoff()
print(result)