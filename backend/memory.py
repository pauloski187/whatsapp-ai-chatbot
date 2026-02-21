"""Simple per-user memory storage without LangChain dependencies."""

from typing import Dict, List


class MemoryManager:
    """Store per-user message history in-memory with a 4-message cap."""

    def __init__(self) -> None:
        """Initialize the user history dictionary."""
        self._memories: Dict[str, List[Dict[str, str]]] = {}

    def get_history(self, user_id: str) -> List[Dict[str, str]]:
        """Return message history for a user, creating empty history if needed."""
        if user_id not in self._memories:
            self._memories[user_id] = []
        self._trim_history(user_id)
        return self._memories[user_id]

    def add_message(self, user_id: str, role: str, content: str) -> None:
        """Append one message and enforce the 4-message limit."""
        history = self.get_history(user_id)
        history.append({"role": role, "content": content})
        self._trim_history(user_id)

    def clear_memory(self, user_id: str) -> None:
        """Delete a user's stored history if it exists."""
        self._memories.pop(user_id, None)

    def _trim_history(self, user_id: str) -> None:
        """Keep only the latest 4 messages for a user."""
        history = self._memories.get(user_id, [])
        if len(history) > 4:
            self._memories[user_id] = history[-4:]


memory_manager = MemoryManager()
