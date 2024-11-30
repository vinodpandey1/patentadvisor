from langchain.schema import BaseChatMessageHistory, ChatMessage
from supabase import create_client
import datetime
import src.service.dbclient as dbclient 

class SupabaseChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.supabase = dbclient.SupabaseDBClient.getClient()

    def add_message(self, message: ChatMessage) -> None:
        """Add a message to the conversation history."""
        self.supabase.table("conversation_history").insert({
            "session_id": self.session_id,
            "role": message.type,
            "message": message.content,
            "timestamp": datetime.datetime.utcnow(),
        }).execute()

    def get_messages(self) -> list[ChatMessage]:
        """Retrieve all messages for the session."""
        response = self.supabase.table("conversation_history") \
            .select("*") \
            .filter("session_id", "eq", self.session_id) \
            .order("timestamp", ascending=True) \
            .execute()

        if response.get("error"):
            raise ValueError(f"Error fetching messages: {response['error']}")

        # Convert rows into ChatMessage objects
        return [ChatMessage(content=row["message"], type=row["role"]) for row in response["data"]]
