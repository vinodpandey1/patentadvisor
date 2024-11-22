
from langchain_chroma import Chroma
from langchain_postgres import PGVector
from service.llm import chatmodel
import chromadb

from service import configReader

def getDBClient():
    database = configReader.getProperty("database")  
    if database == "chroma":
        persist_directory=configReader.getDatabaseDir()
        return ChromaDBClient.get_collection(persist_directory)
    if database == "postgres":
        return PostgreSQLDBClient.get_collection()

class ChromaDBClient:
    _client = None
    _collection = None
    _vectorStore = None
    
    @staticmethod
    def get_collection(persist_directory,collection_name="patentdocuments"):
            
        if ChromaDBClient._client is None:
            emb_fn = chatmodel.getEmbeddingFunction("openai-embedding")
            embeddings = chatmodel.getEmbedding("openai-embedding")
            ChromaDBClient._client = chromadb.PersistentClient(path=persist_directory)
            ChromaDBClient._collection = ChromaDBClient._client.get_or_create_collection(collection_name,embedding_function=emb_fn)
            ChromaDBClient._vectorStore = Chroma(
             client=ChromaDBClient._client,
             collection_name=collection_name,
             embedding_function=embeddings,
            )
        return ChromaDBClient._client,ChromaDBClient._collection,ChromaDBClient._vectorStore
 
class PostgreSQLDBClient:
    _client = None
    _collection = None
    _vectorStore = None
    
    @staticmethod
    def get_collection(collection_name="patentdocuments"):
            
       
        if PostgreSQLDBClient._client is None:
            embeddings = chatmodel.getEmbedding("openai-embedding")
            PostgreSQLDBClient._client = configReader.getProperty("postgreSQLURL")
            PostgreSQLDBClient._vectorStore = PGVector(
             connection=PostgreSQLDBClient._client,
             collection_name=collection_name,
             embeddings=embeddings,
             use_jsonb=True,
            )
        return PostgreSQLDBClient._client,PostgreSQLDBClient._collection,PostgreSQLDBClient._vectorStore