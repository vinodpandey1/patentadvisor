
import src.service.llm.chatmodel as chatmodel
from src.service import configReader, dbclient
from src.service.document import storeDocument
from src.service.metadataextraction import metadatainfo
from src.service.llm.chatmodel import getChatModel
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_community.query_constructors.chroma import ChromaTranslator
from langchain_community.query_constructors.pgvector import  PGVectorTranslator
from src.utils import logger
from src.service.document.bias_analyser import BiasAnalyser
from src.service.document.chatHistory import SupabaseChatMessageHistory  
import json
from langchain.chains.query_constructor.base import (
    StructuredQueryOutputParser,
    get_query_constructor_prompt,
    load_query_constructor_runnable,
)
from src.llmtemplate.template import DOCUMENT_QUERY_TEMPLATE
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain


def searchDocument(query):

    
    logger.info("fetching similarity search results")
   
    database = configReader.getProperty("database")  
    if database == "postgres":
        results= getSearchResultsFromPostgresql(query)
    if database == "supabase":
        results=getSearchResultFromSupabase(query)
   
    documentList=[]
    documentIdList=[]

    for doc in results: 
        
        page_content = doc['page_content']
        
        logger.debug(f"Fetched Patent Content {page_content}")
        id = doc['id']
        logger.info(f"Fetched Documetn ID {id}")
        metadata=doc['metadata']
        logger.debug(f"Fetched Metadata  {metadata}")
        
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        if id is not None:
            patentId = id.split("_")[0]
        else:
            patentId = metadata.get('patentnumber')
        if(patentId not in documentIdList):
            logger.info(f"Patent Id {patentId}")
            metadata['filename'] = f"{patentId}.pdf"
            documentList.append(metadata)
            documentIdList.append(patentId)
    return documentList
        
def queryDocument(query, documentID):
    
    logger.info(f"Searching from patent document {documentID}")
    
    database = configReader.getProperty("database")  
    if database == "supabase":
        results=queryDocumentFromSupabase(query)

    llm_response = get_llm_response(results)
    logger.info(llm_response)
    logger.info(BiasAnalyser.analyze_sentiment_and_bias(llm_response))
    return llm_response
    

def getQueryStructure(query):
    
    document_content_description = "Patent Detail"
    
    prompt = get_query_constructor_prompt(
    document_contents = document_content_description,
    attribute_info = metadatainfo.metadata_field_info, 
    allowed_comparators=['lte', 'exists', 'ne', 'or', 'gt', 'eq', 'and', 'gte', 'nin', 'not', 'like', 'ilike', 'in', '$lt', 'between']
    )
    
    logger.debug(f"Promot for query translater Id {prompt}")
    llm = getChatModel("gpt-4")
    llm.temperature = 0
    output_parser = StructuredQueryOutputParser.from_components()
    query_constructor = prompt | llm | output_parser
    
    result = query_constructor.invoke(
        {
        "query": query
        }
    )

    if(result.filter is not None):
        structured_query_translator=PGVectorTranslator()
        structureQuery = structured_query_translator.visit_structured_query(result)
        logger.info(structureQuery)
        filter = extract_filter_from_tuple(structureQuery)
        filter = update_operators(filter)
        logger.info("Filter :",filter)
        return filter
    return None
   
    # chain = load_query_constructor_runnable(
    # llm = llm, document_contents = document_content_description,
    # attribute_info = metadatainfo.metadata_field_info)
    
    
    # print(chain.invoke(
    #     {
    #     "query": query
    #     }
    # ))
    
def extract_filter_from_tuple(result):
    if isinstance(result, tuple) and len(result) == 2:
        _, filter_dict = result
        if 'filter' in filter_dict:
            return filter_dict['filter']
    return None

def update_operators(filter_dict):
    valid_operators = ["eq", "neq", "gt", "lt", "gte", "lte", "like", "ilike"] 
    updated_filter = {}
    for key, value in filter_dict.items():
        if isinstance(value, dict):
            updated_value = {}
            for op, val in value.items():
                if op in valid_operators:                    
                    if op == "like":
                        val = f"%{val}%"
                    updated_value[f"${op}"] = val
            updated_filter[key] = updated_value
    
    return updated_filter


def getSearchResultFromSupabase(query):
    try:
        client, collection, vector_store = dbclient.getDBClient("patentdocuments")
        embeddings = chatmodel.getEmbedding("openai-embedding")
        query_vector = embeddings.embed_query(query )
        results = client.rpc("match_documents_native", {"query_embedding": query_vector, "match_threshold": 0.5,"match_count": 5}
            ).execute()
        return results.data
    except Exception as e:
        logger.error(f"Error in Supabase Search: {e}")
        return None


def getSearchResultsFromPostgresql(query):
    try:
        client, collection, vector_store = dbclient.getDBClient("patentdocuments")
        filter_dict=getQueryStructure(query)
        logger.info(filter_dict)
        results = vector_store.similarity_search(
            query=query, k=1, filter=filter_dict, where_document=filter_dict, verbose=True
        )
        return results
    except Exception as e:
        logger.error(f"Error in Postgres Search: {e}")
        return None

def queryDocumentFromSupabase(query, documentId):
    try:
        client, collection, vector_store = dbclient.getDBClient("patentdocumentdetail")
        embeddings = chatmodel.getEmbedding("openai-embedding")
        query_vector = embeddings.embed_query(query )
        results = client.rpc("match_documents_detail", {"query_embedding": query_vector, "match_threshold": 0.5,"match_count": 5, "documentId":documentId}
            ).execute()
        return results.data
    except Exception as e:
        logger.error(f"Error in Supabase Search: {e}")
        return None

def selfRetrivel(query):
  
    # this is example and not being used
    client, collection, vector_store = dbclient.getDBClient("patentdocuments")
    
    lst = ['US10282512B2']
    filter_dict = {'TechnologyKeywords': {'$like': '%Digital Music%'}}
    
    llm = getChatModel("gpt-4")
    llm.temperature = 0
    
    document_content_description = "Patent Detail"
    self_retriever = SelfQueryRetriever.from_llm(
    llm = llm,
    vectorstore = vector_store,
    document_contents = document_content_description,
    metadata_field_info = metadatainfo.metadata_field_info,
    structured_query_translator=PGVectorTranslator(),
    verbose=True
    )
    
def get_llm_response(context, query, sessionId="383738uiihfi"):


    # prompt = DOCUMENT_QUERY_TEMPLATE.format(context=context, query=query)

    message_history = SupabaseChatMessageHistory(
    session_id=sessionId,
    )
    
    memory = ConversationBufferMemory(chat_memory=message_history, return_messages=True)

# Initialize a language model (e.g., OpenAI GPT-3.5)
    llm = getChatModel("gpt-3.5-turbo")
    llm.temperature = 0.5

# Create a conversation chain
    conversation = ConversationChain(llm=llm, memory=memory, prompt=DOCUMENT_QUERY_TEMPLATE)

# Simulate a conversation
    response = conversation.predict(input=query, context=context)
    print("Bot:", response)

    # Fetch the conversation history
    for msg in message_history.get_messages():
        print(f"[{msg.type}] {msg.content}")
        
        return response.content
