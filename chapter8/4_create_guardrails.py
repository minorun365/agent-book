import boto3

from dotenv import load_dotenv
load_dotenv(

def create_code_name_guardrail():
    bedrock_client = boto3.client("bedrock")
    # Bedrock Guardraidsを構築
    response = bedrock_client.create_guardrail(
        name="CodeNameGuardrail",
        description="Guardrail to block service code name",
        wordPolicyConfig={
            "wordsConfig": [ # NGワードの定義
                {"text": "Orion"},
                {"text": "Falcon"},
                {"text": "Mercury"},
                {"text": "Athena"},
                {"text": "Sentinel"},
            ],
        },
        blockedInputMessaging="NGワードを含むため、ブロックしました。",
        blockedOutputsMessaging="NGワードを含むため、ブロックしました。"
    )
    # 作成したガードレールのメタ情報の出力
    print("Created guardrail:")
    print(f"ID : {response["guardrailId"]}")
    print(f"ARN: {response["guardrailArn"]}")
    print(f"Version: {response["version"]}")

create_code_name_guardrail()
