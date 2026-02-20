"""Escalation and human handoff detection utilities."""


class HandoffService:
    """Detect escalation intent and provide a standard handoff response."""

    ESCALATION_PHRASES = [
        "talk to human",
        "speak to agent",
        "real person",
        "customer service",
        "help me please",
        "not helpful",
    ]

    def check_handoff(self, message: str) -> bool:
        """Return True if an escalation phrase appears in the message."""
        lowered = message.lower()
        return any(phrase in lowered for phrase in self.ESCALATION_PHRASES)

    def get_handoff_message(self) -> str:
        """Return the fixed message shown when escalation is triggered."""
        return "I'm connecting you with a human agent now. Please hold on — someone will be with you shortly."


handoff_service = HandoffService()
