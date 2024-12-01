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
        
        current_timestamp = datetime.datetime.utcnow().isoformat()
        logger.info(current_timestamp)
        
        self.supabase.table("conversation_history").insert({
            "session_id": self.session_id,
            "document_id": self.documentId,
            "role": message.type,
            "message": message.content,
            "timestamp": current_timestamp,
        }).execute()

    def get_messages(self) -> list[ChatMessage]:
        """Retrieve all messages for the session."""
        logger.info(f"Fetching messages for session {self.session_id}")
        try:
            response = self.supabase.table("conversation_history") \
                .select("*") \
                .filter("session_id", "eq", self.session_id) \
                .filter("document_id", "eq", self.documentId) \
                .order("timestamp", desc=True) \
                .limit(10) \
                .execute() 
            # logger.info(f"Response: {response}")
        except Exception as e:
            raise ValueError(f"Error fetching messages: {e}")

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
