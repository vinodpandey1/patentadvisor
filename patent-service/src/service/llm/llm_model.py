import os

from langchain_openai import ChatOpenAI
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from src.llmtemplate.modelconfig import MODEL_CONFIGS, API_KEY_CONFIG
from langchain_openai import OpenAIEmbeddings


def get_chat_model(model: str):

    modelName = MODEL_CONFIGS[model]

    if modelName is None:
        print(f"Model {model} not found in model config. Returning Default Model")
        llm_chat = ChatOpenAI(model_name=modelName, temperature=0.7,openai_api_key=get_api_key(modelName))
        return llm_chat

    else:

        if model.startswith("gpt-"):
            llm_chat = ChatOpenAI(model_name=modelName, temperature=0.7,openai_api_key=get_api_key(modelName))
            return llm_chat

        elif model.startswith("Zephyr"):

            llm = HuggingFaceEndpoint(
                repo_id=modelName,
                task="text-generation"
            )
            llm_chat = ChatHuggingFace(llm = llm)
            return llm_chat


def get_api_key(model: str):

    keyName = API_KEY_CONFIG[model]
    key = os.getenv(keyName)
    if key is None:
        print(f"API Key for {model} not found in environment variables")
    else:
        return key


def get_embedding(model: str):
    model_name = MODEL_CONFIGS[model]
    embeddings = OpenAIEmbeddings(
                api_key=get_api_key(model),
                model=model_name
            )
    return embeddings
