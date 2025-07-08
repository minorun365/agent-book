import boto3
import os
from dotenv import load_dotenv
load_dotenv("/workspaces/agent-book/.env")

def create_bedrock_attack_guardrail():
    bedrock_client = boto3.client('bedrock')
    aws_account_id = boto3.client('sts').get_caller_identity()["Account"]
    region = os.getenv("AWS_DEFAULT_REGION")

    response = bedrock_client.create_guardrail(
        name='PromptInjectionGuardrail',
        # コンテンツフィルターの設定
        contentPolicyConfig={
            'filtersConfig': [
                {
                    'type': 'PROMPT_ATTACK',
                    'inputStrength': 'HIGH',
                    'inputAction': 'BLOCK',
                    'outputStrength': 'NONE',
                    'outputAction': 'NONE',
                    'inputEnabled': True,
                    'outputEnabled': False, 
                    'inputModalities': ['TEXT'],
                    'outputModalities': ['TEXT']
                },
            ],
            'tierConfig': {
                'tierName': 'STANDARD'
            }
        },
        crossRegionConfig={
            'guardrailProfileIdentifier': f'arn:aws:bedrock:{region}:{aws_account_id}:guardrail-profile/us.guardrail.v1:0'
        },
        # ブロック時のメッセージ
        blockedInputMessaging='攻撃を検知しました。ブロックします。',
        blockedOutputsMessaging='攻撃を検知しました。ブロックします。',
    )
    print("Created guardrail:")
    print(f"ID : {response['guardrailId']}")
    print(f"ARN: {response['guardrailArn']}")
    print(f"Version: {response['version']}")

create_bedrock_attack_guardrail()

# Created guardrail:
# ID : 1tawzd406eby
# ARN: arn:aws:bedrock:us-east-1:654654377904:guardrail/1tawzd406eby
# Version: DRAFT