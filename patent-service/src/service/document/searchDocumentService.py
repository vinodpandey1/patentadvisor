
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


def searchDocument(query):

    client, collection, vector_store = dbclient.getDBClient()
   
    lst = ['US10282512B2']
    filter_dict = {'PatentNumber':'US10282512B2'}
    
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
    # print("Self Retriever Result")
    # print(self_retriever.invoke(query))
    
    
    retriever = vector_store.as_retriever(
    search_type="mmr", search_kwargs={"k": 1, 'filter':filter_dict}
    )
    results = retriever.invoke(query)
    
    print("fetching results")
    for result in results:
        print("\n")
        print(result)
  
    print("fetching similarity search results")
    results = vector_store.similarity_search(
        query=query, k=1
    )
    for doc in results: 
        print(f"* [{doc.metadata}]")
    
def getDocument(id):
     client, collection, vector_store = dbclient.getDBClient()
     collection.get(id,include=['metadatas'])

def getQueryStructure(query):
    
    document_content_description = "Patent Detail"
    
    prompt = get_query_constructor_prompt(
    document_contents = document_content_description,
    attribute_info = metadatainfo.metadata_field_info,    
    )
    
    llm = getChatModel("gpt-4")
    llm.temperature = 0
    output_parser = StructuredQueryOutputParser.from_components()
    query_constructor = prompt | llm | output_parser
    
    print(query_constructor.invoke(
        {
        "query": query
        }
    ))
    
    # chain = load_query_constructor_runnable(
    # llm = llm, document_contents = document_content_description,
    # attribute_info = metadatainfo.metadata_field_info)
    
    
    # print(chain.invoke(
    #     {
    #     "query": query
    #     }
    # ))
    
