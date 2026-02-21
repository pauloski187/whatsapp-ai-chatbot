"""Session memory management keyed by user IDs."""

from typing import Dict

from langchain_community.memory import ConversationBufferMemory


class MemoryManager:
    """Manage per-user conversation memory with bounded message history."""

    def __init__(self) -> None:
        """Initialize the in-memory store for user sessions."""
        self._memories: Dict[str, ConversationBufferMemory] = {}

    def get_memory(self, user_id: str) -> ConversationBufferMemory:
        """Get or create memory for a user and enforce a 4-message limit."""
        if user_id not in self._memories:
            self._memories[user_id] = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                input_key="input",
                output_key="output",
            )
        self.trim_history(user_id)
        return self._memories[user_id]

    def clear_memory(self, user_id: str) -> None:
        """Delete a user's memory session if it exists."""
        self._memories.pop(user_id, None)

    def trim_history(self, user_id: str) -> None:
        """Keep only the last 4 message objects in the user chat history."""
        memory = self._memories.get(user_id)
        if memory is None:
            return
        history = memory.chat_memory.messages
        if len(history) > 4:
            memory.chat_memory.messages = history[-4:]


memory_manager = MemoryManager()
