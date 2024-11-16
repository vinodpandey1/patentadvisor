import os
import openai


from langchain_openai import ChatOpenAI
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from llmtemplate.modelconfig import MODEL_CONFIGS, API_KEY_CONFIG
import chromadb.utils.embedding_functions as embedding_functions

def getChatModel(model:str):
    
    modelName = MODEL_CONFIGS[model]
    
    if modelName is None:
        print(f"Model {model} not found in model config. Returning Default Model")
        llm_chat = ChatOpenAI(model_name=modelName, temperature=0.7,openai_api_key=getAPIKey(modelName))
        return llm_chat
    
    else:    
    
        if(model.startswith("gpt-")):
            llm_chat = ChatOpenAI(model_name=modelName, temperature=0.7,openai_api_key=getAPIKey(modelName))
            return llm_chat
        
        elif(model.startswith("Zephyr")):
            
            llm = HuggingFaceEndpoint(
            repo_id=modelName,
            task="text-generation"
            )
            llm_chat = ChatHuggingFace(llm = llm)
            return llm_chat


def getAPIKey(model:str):
    
    keyName = API_KEY_CONFIG[model]
    key = os.getenv(keyName)
    if(key is None):
        print(f"API Key for {model} not found in environment variables")
    else:
        return key

def getEmbeddingFunction(model:str):
    modelName = MODEL_CONFIGS[model]
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=getAPIKey(model),
                model_name=modelName
            )
    return openai_ef
    
