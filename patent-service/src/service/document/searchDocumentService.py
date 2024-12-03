
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
from langchain_community.callbacks import ClearMLCallbackHandler
from langchain_core.callbacks import StdOutCallbackHandler  
import json
import uuid
from langchain.chains.query_constructor.base import (
    StructuredQueryOutputParser,
    get_query_constructor_prompt,
    load_query_constructor_runnable,
)
from clearml import Task 
from src.llmtemplate.template import DOCUMENT_QUERY_TEMPLATE
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage


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
        logger.info(f"Fetching Document {doc}")
        page_content = doc['page_content']
        
        logger.debug(f"Fetched Patent Content {page_content}")
        id = doc['id']
        logger.info(f"Fetched patent ID {id}")
        document_id = doc['document_id']
        logger.info(f"Fetched patent ID {document_id}")
        metadata=doc['metadata']
        logger.debug(f"Fetched Metadata  {metadata}")
        
        similarity=doc['similarity']
        similarity = round(similarity, 3)
        
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
            
            metadata['documentId'] = document_id
            metadata['similarity_score'] = similarity
            assignees = metadata.get('assignees')
            if isinstance(assignees, str):
                metadata['assignees'] = [assignees]
            
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
        
def queryDocument(query, userid, documentID):
    
    logger.info(f"Searching from patent document {documentID}")
    
    database = configReader.getProperty("database")  
    if database == "supabase":
        try:
            results=queryDocumentFromSupabase(query,documentID)
            logger.info("Successfully fetched data from database")
        except Exception as e:
            logger.error(f"Failed after retries: {e}")
            raise

    llm_response,history_dict = get_llm_response_for_document_search(results, query, userid, documentID)
    # logger.info(llm_response)
    bias_analyzer = BiasAnalyser.analyze_sentiment_and_bias(llm_response)
    return llm_response , history_dict, bias_analyzer
 
def getConversationHistory(userId, documentID):
    
    logger.info(f"Get getConversationHistory for document {documentID}")
    message_history = SupabaseChatMessageHistory(
        session_id=userId,
        documentId=documentID
    )
    chat_history = message_history.get_messages()
    
    if len(chat_history) > 1:
        chat_history.reverse()
        history_dict = [{"role": msg.role, "content": msg.content} for msg in chat_history[0:10]]
    else:
        history_dict=[{}]
    return history_dict
        
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
    max_retries = 3
    delay = 2
    for attempt in range(max_retries):
        try:
            client, collection, vector_store = dbclient.getDBClient("patentdocuments")
            embeddings = chatmodel.getEmbedding("openai-embedding")
            query_vector = embeddings.embed_query(query)
            results = client.rpc("match_documents_native", {
                "query_embedding": query_vector,
                "match_threshold": 0.2,
                "match_count": 5
            }).execute()
            logger.info(results.data)
            return results.data
        except Exception as e:
            logger.info(e)
            if hasattr(e, 'errno') and e.errno == errno.ECONNRESET:
                logger.error(f"Connection reset by peer: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    logger.error("Max retries reached. Failing.")
                    raise
            else:
                logger.error(f"Error in Supabase Search: {e}")
                raise


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
    max_retries = 3
    delay = 2
    for attempt in range(max_retries):
        try:
            client, collection, vector_store = dbclient.getDBClient("patentdocumentdetail")
            embeddings = chatmodel.getEmbedding("openai-embedding")
            query_vector = embeddings.embed_query(query)
            
            # Ensure the documentId is formatted as a UUID
            document_uuid = str(uuid.UUID(documentId))
            
            results = client.rpc("match_documents_detail", {
                "query_embedding": query_vector,
                "match_threshold": 0.1,
                "match_count": 5,
                "documentid": document_uuid
            }).execute()
            
            return results.data
        except Exception as e:
            logger.info(e)
            if hasattr(e, 'errno') and e.errno == errno.ECONNRESET:
                logger.error(f"Connection reset by peer: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    logger.error("Max retries reached. Failing.")
                    raise
            else:
                logger.error(f"Error in Supabase Search: {e}")
                raise

    
def get_llm_response_for_document_search(contextValue, query, userId, documentId):
 

    message_history = SupabaseChatMessageHistory(
        session_id=userId,
        documentId=documentId
    )
   
    chat_history = message_history.get_messages()
    # logger.info(f"chat history {chat_history}")
    if len(chat_history) > 1:
        history = "\n".join([f"{msg.role}: {msg.content}" for msg in chat_history[0:4]])
        history_dict = [{"role": msg.role, "content": msg.content} for msg in chat_history[0:5]]
    else:
        history = "first message" 
        history_dict=[{}]
    
    # logger.info(f"History {history_dict}") 

    prompt  = DOCUMENT_QUERY_TEMPLATE.format(context=contextValue,input=query, history=history)
    
    # logger.info(prompt)
    llm = getChatModel("gpt-3.5-turbo")
    llm.temperature = 0
    # llm.callback = callbacks
    response = llm.invoke(prompt)
    # logger.info(response.content)
    
    # clearml_callback.flush_tracker(langchain_asset=llm, name="Document Search Response")
    
    message_history.add_messages([
        AIMessage(content=response.content),
        HumanMessage(content=query),
    ])
    return response.content, history_dict



# clearml_callback = ClearMLCallbackHandler(
#     task_type="inference",                        # task_type – The type of ClearML task to create eg. training, testing, inference, etc
#                                                   # This helps to further organize projects and ensure tasks are easy to search and find.
#     project_name= "patentsearch",
#     task_name= "documentsearch",                  # task_name – The name of the task to create
#     tags=["test"],                                # tags – A list of tags to add to the task
#     # Change the following parameters based on the amount of detail you want tracked
#     visualize=True,                               # visualize - Set to True for ClearML to capture the run's Dependencies and Entities plots to the ClearML task
#     complexity_metrics=False,                     # complexity_metrics - Set to True to log complexity metrics
#     stream_logs=False                             # stream_logs - Set to True to stream callback actions to ClearML Parameters.
# )

# callbacks = [StdOutCallbackHandler(), clearml_callback]