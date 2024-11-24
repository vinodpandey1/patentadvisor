
from service import configReader, dbclient
from service.document import storeDocument
from service.metadataextraction import metadatainfo
from service.llm.chatmodel import getChatModel
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_community.query_constructors.chroma import ChromaTranslator
from langchain_community.query_constructors.pgvector import  PGVectorTranslator
from langchain.chains.query_constructor.base import (
    StructuredQueryOutputParser,
    get_query_constructor_prompt,
    load_query_constructor_runnable,
)
from langchain_core.structured_query import (
    Comparator,
    Comparison,
    FilterDirective,
    Operation,
    Operator,
    StructuredQuery,
)

def searchDocument(query):

    client, collection, vector_store = dbclient.getDBClient("patentdocuments")
   
    lst = ['US10282512B2']
    # filter_dict = {'TechnologyKeywords': {'$like': '%Digital Music%'}}
    
    llm = getChatModel("gpt-4")
    llm.temperature = 0
    
    # document_content_description = "Patent Detail"
    # self_retriever = SelfQueryRetriever.from_llm(
    # llm = llm,
    # vectorstore = vector_store,
    # document_contents = document_content_description,
    # metadata_field_info = metadatainfo.metadata_field_info,
    # structured_query_translator=PGVectorTranslator(),
    # verbose=True
    # )
    # print("Self Retriever Result")
    # print(self_retriever.invoke(query))
    
    
    # retriever = vector_store.as_retriever(
    # search_type="mmr", search_kwargs={"k": 1, 'filter':filter_dict}
    # )
    # results = retriever.invoke(query)
    
    # print("fetching results")
    # for result in results:
    #     print("\n")
    #     print(result)
  
    print("fetching similarity search results")
    filter_dict=getQueryStructure(query)
    results = vector_store.similarity_search(
        query=query, k=10, filter=filter_dict, where_document=filter_dict, verbose=True
    )
    documentList=[]
    documentIdList=[]
    # print(results)
    for doc in results: 
        print(f"* [{doc.page_content}]")
        print(f"* [{doc.id}]")
        
        patentId = doc.id.split("_")[0]
        if(patentId not in documentIdList):
            print("PatentID:",patentId)
            documentList.append(doc.metadata)
            data = doc.metadata
            data['filename'] = f"{patentId}.pdf"
            documentIdList.append(patentId)
    return documentList
        
        
    
def getDocument(id):
     client, collection, vector_store = dbclient.getDBClient("patentdocuments")
     collection.get(id,include=['metadatas'])

def getQueryStructure(query):
    
    document_content_description = "Patent Detail"
    
    prompt = get_query_constructor_prompt(
    document_contents = document_content_description,
    attribute_info = metadatainfo.metadata_field_info, 
    allowed_comparators=['lte', 'exists', 'ne', 'or', 'gt', 'eq', 'and', 'gte', 'nin', 'not', 'like', 'ilike', 'in', '$lt', 'between']
    )
    
    # print(prompt)
    llm = getChatModel("gpt-4")
    llm.temperature = 0
    output_parser = StructuredQueryOutputParser.from_components()
    query_constructor = prompt | llm | output_parser
    
    result = query_constructor.invoke(
        {
        "query": query
        }
    )
    print(result)
    if(result.filter is not None):
        structured_query_translator=PGVectorTranslator()
        structureQuery = structured_query_translator.visit_structured_query(result)
        print(structureQuery)
        filter = extract_filter_from_tuple(structureQuery)
        filter = update_operators(filter)
        print("Filter :",filter)
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