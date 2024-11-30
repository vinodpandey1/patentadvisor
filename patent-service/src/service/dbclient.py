
from langchain_chroma import Chroma
from langchain_postgres import PGVector
from src.service.llm import chatmodel
import chromadb
from src.utils import logger
import os
from src.service import configReader
from supabase import create_client

from langchain_community.vectorstores import SupabaseVectorStore

def getDBClient(collectionName):
    

    if collectionName is None:
        collectionName = "patentdocuments"
    database = configReader.getProperty("database")  
    if database == "chroma":
        persist_directory=configReader.getDatabaseDir(collectionName)
        return ChromaDBClient.get_collection(persist_directory)
    if database == "postgres":
        return PostgreSQLDBClient.get_collection(collectionName)
    if database == "supabase":
        return SupabaseDBClient.get_collection(collectionName)

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
    def get_collection(collection_name):
            
        embeddings = chatmodel.getEmbedding("openai-embedding")
        PostgreSQLDBClient._client = configReader.getProperty("postgreSQLURL")
        
        PostgreSQLDBClient._vectorStore = PGVector(
             connection=PostgreSQLDBClient._client,
             collection_name=collection_name,
             embeddings=embeddings,
             use_jsonb=True,
            )   
        return PostgreSQLDBClient._client,PostgreSQLDBClient._collection,PostgreSQLDBClient._vectorStore
    
class SupabaseDBClient:
    _client = None
    _collection = None
    _vectorStore = None
    
    @staticmethod
    def getClient():
        if SupabaseDBClient._client is None:
            SupabaseDBClient._client = initialize_supabase()
        return SupabaseDBClient._client
    
    def get_collection(collection_name):
            
        embeddings = chatmodel.getEmbedding("openai-embedding")
        SupabaseDBClient._client = initialize_supabase()
        
        SupabaseDBClient._vectorStore = SupabaseVectorStore(
             client=SupabaseDBClient._client,
             table_name=collection_name,
             embedding=embeddings, 
        )   
        
        return SupabaseDBClient._client,SupabaseDBClient._collection,SupabaseDBClient._vectorStore
    
def initialize_supabase():
    """
    Initializes the Supabase client using credentials from the .env file.
    
    Returns:
        Client: Supabase client instance.
    """
    try:
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not all([supabase_url, supabase_key]):
            logger.info("Supabase credentials are missing in the .env file.")
            return None
        
        supabase = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized successfully.")
        return supabase
    
    except Exception as e:
        logger.info(f"Failed to initialize Supabase client: {e}")
        return None