import os

from langchain_community.vectorstores import SupabaseVectorStore
import src.service.llm.llm_model as llm_model
from supabase import create_client, Client

import logging
from logging import config

import src.constants as const

config.fileConfig(const.CONFIG_DIR + "/logging.conf")
logger = logging.getLogger("patent")


class SupabaseClient:
    _client = None
    _collection = None
    _vectorStore = None

    @staticmethod
    def get_collection(collection_name):
        embeddings = llm_model.get_embedding("openai-embedding")
        SupabaseClient._client = initialize_supabase()

        SupabaseClient._vectorStore = SupabaseVectorStore(
            client=SupabaseClient._client,
            table_name=collection_name,
            embedding=embeddings,
        )

        return SupabaseClient._client, SupabaseClient._collection, SupabaseClient._vectorStore


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
            logger.error("Supabase credentials are missing in the .env file.")
            raise ValueError("Supabase credentials are missing.")

        supabase = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized successfully.")
        return supabase

    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        return None
