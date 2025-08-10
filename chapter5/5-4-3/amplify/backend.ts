import { defineBackend } from "@aws-amplify/backend";
import { auth } from "./auth/resource";
import { ManagedPolicy } from "aws-cdk-lib/aws-iam";


const backend = defineBackend({
    auth,
});


// 認証済みユーザーのIAM Roleを取得
const authenticatedUserIamRole =
    backend.auth.resources.authenticatedUserIamRole;


// Bedrock用のAWSマネージドポリシーを追加
authenticatedUserIamRole.addManagedPolicy(
    ManagedPolicy.fromAwsManagedPolicyName("AmazonBedrockFullAccess")
);
