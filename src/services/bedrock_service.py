# bedrock_service.py

import boto3
import json
from .config import load_config

config = load_config()

client = boto3.client(
    "bedrock-runtime",
    region_name=config["aws_region"],
    aws_access_key_id=config["aws_access_key_id"],
    aws_secret_access_key=config["aws_secret_access_key"]
)

def call_llama4(prompt: str):
    response = client.invoke_model(
        modelId=config["bedrock_model_id"],
        contentType="application/json",
        accept="application/json",
        body=json.dumps({
            "prompt": prompt,
            "max_gen_len": config["llm_defaults"]["max_tokens"],
            "temperature": config["llm_defaults"]["temperature"],
            "top_p": config["llm_defaults"]["top_p"]
        })
    )

    result = json.loads(response["body"].read())
    return result["generation"] if "generation" in result else result
