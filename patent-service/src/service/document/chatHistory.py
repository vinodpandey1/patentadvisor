from langchain.schema import BaseChatMessageHistory, ChatMessage
from supabase import create_client
import datetime
import src.service.dbclient as dbclient 
from langchain_postgres import PostgresChatMessageHistory
from src.utils import logger

class SupabaseChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, session_id: str, documentId:str):
        self.session_id = session_id
        self.documentId = documentId
        self.supabase = dbclient.SupabaseDBClient.getClient()

    def add_message(self, message: ChatMessage) -> None:
        logger.info("Add a message to the conversation history.")
        
        max_retries = 3
        delay = 2
        current_timestamp = datetime.datetime.utcnow().isoformat()
        for attempt in range(max_retries):
            try:
                self.supabase.table("conversation_history").insert({
                    "session_id": self.session_id,
                    "document_id": self.documentId,
                    "role": message.type,
                    "message": message.content,
                    "timestamp": current_timestamp,
                }).execute()
                return
            except Exception as e:
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
                    logger.error(f"Error in Supabase operation: {e}")
                    raise

    def get_messages(self) -> list[ChatMessage]:
        """Retrieve all messages for the session."""
        logger.info(f"Fetching messages for session {self.session_id}")
        max_retries = 3
        delay = 2
        for attempt in range(max_retries):
            try:
                response = self.supabase.table("conversation_history") \
                    .select("*") \
                    .filter("session_id", "eq", self.session_id) \
                    .filter("document_id", "eq", self.documentId) \
                    .order("timestamp", desc=True) \
                    .limit(5) \
                    .execute()
                logger.info(f"Response: {response}")
                break
            except Exception as e:
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
                    logger.error(f"Error fetching messages: {e}")
                    raise

        # Convert rows into ChatMessage objects
        # if response.error:
        #     raise ValueError(f"Error fetching messages: {response.error.message}")
        
        if not response.data:
            return []
        else:
            return [ChatMessage(content=row["message"], role=row["role"], tye="chat") for row in response.data]

    def clear(self) -> None:
        """Clear all messages for the session."""
        self.supabase.table("conversation_history") \
            .delete() \
            .filter("session_id", "eq", self.session_id) \
            .execute()
