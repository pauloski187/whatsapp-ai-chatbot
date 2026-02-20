"""Chat orchestration service using Groq, RAG, memory, leads, and handoff."""

from typing import List

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from config import settings
from database import get_collection, query_similar
from handoff import handoff_service
from leads import lead_service
from memory import memory_manager


class ChatService:
    """Generate responses by combining retrieval context and conversation state."""

    def __init__(self) -> None:
        """Initialize shared resources for chat requests."""
        self.collection = get_collection(settings.CHROMA_COLLECTION_NAME)

    def _build_system_prompt(self, context_chunks: List[str]) -> str:
        """Create a system prompt from business settings and retrieved context."""
        context_block = "\n\n".join(context_chunks) if context_chunks else "No specific knowledge found."
        return (
            f"You are the AI customer support assistant for {settings.BUSINESS_NAME}.\n"
            f"Tone: {settings.BOT_TONE}.\n"
            "Use the context below when relevant. If context is missing, be transparent and helpful.\n\n"
            f"Context:\n{context_block}"
        )

    def _build_history_messages(self, user_id: str) -> List[HumanMessage | AIMessage]:
        """Convert stored message history into LangChain message objects."""
        history = memory_manager.get_history(user_id)
        messages: List[HumanMessage | AIMessage] = []
        for item in history:
            role = item.get("role", "")
            content = item.get("content", "")
            if not content:
                continue
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))
        return messages

    def get_reply(self, user_id: str, message: str, platform: str = "web") -> str:
        """Return an assistant reply for a user message."""
        lead_data = lead_service.detect_lead_info(message)
        if lead_data:
            try:
                lead_service.save_lead(platform=platform, user_id=user_id, data_dict=lead_data)
            except Exception:
                pass

        if handoff_service.check_handoff(message):
            handoff_text = handoff_service.get_handoff_message()
            memory_manager.add_message(user_id, "user", message)
            memory_manager.add_message(user_id, "assistant", handoff_text)
            return handoff_text

        history_messages = self._build_history_messages(user_id)
        self.collection = get_collection(settings.CHROMA_COLLECTION_NAME)
        context_chunks = query_similar(self.collection, message, n=4)
        system_prompt = self._build_system_prompt(context_chunks)

        model = ChatGroq(
            model_name=settings.GROQ_MODEL_NAME,
            groq_api_key=settings.GROQ_API_KEY,
        )
        message_stack = [SystemMessage(content=system_prompt), *history_messages, HumanMessage(content=message)]
        response = model.invoke(message_stack)
        reply_text = response.content if isinstance(response.content, str) else str(response.content)

        memory_manager.add_message(user_id, "user", message)
        memory_manager.add_message(user_id, "assistant", reply_text)
        return reply_text


chat_service = ChatService()
