from typing import Any, Dict, Optional, List
import json

class AgentMessage:
    """
    Represents a message sent between agents.
    """
    def __init__(self,
                 sender_id: str,
                 recipient_id: str,
                 message_type: str,
                 payload: Dict[str, Any],
                 task_id: Optional[str] = None):
        """
        Initializes an AgentMessage.

        Args:
            sender_id: The ID of the agent sending the message.
            recipient_id: The ID of the agent receiving the message.
            message_type: The type of message (e.g., "task_request", "task_result", "feedback").
            payload: A dictionary containing the message content.
            task_id: Optional ID of the task related to this message.
        """
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.message_type = message_type
        self.payload = payload
        self.task_id = task_id

    def to_dict(self) -> Dict[str, Any]:
        """Converts the message to a dictionary."""
        return {
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "message_type": self.message_type,
            "payload": self.payload,
            "task_id": self.task_id
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentMessage":
        """Creates an AgentMessage from a dictionary."""
        return cls(
            sender_id=data["sender_id"],
            recipient_id=data["recipient_id"],
            message_type=data["message_type"],
            payload=data["payload"],
            task_id=data.get("task_id")
        )

    def to_json(self) -> str:
        """Converts the message to a JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_string: str) -> "AgentMessage":
        """Creates an AgentMessage from a JSON string."""
        return cls.from_dict(json.loads(json_string))

    def __repr__(self) -> str:
        return (f"AgentMessage(sender_id='{self.sender_id}', recipient_id='{self.recipient_id}', "
                f"message_type='{self.message_type}', task_id='{self.task_id}', "
                f"payload_keys={list(self.payload.keys())})")

# A simple placeholder for an inter-agent communication channel
# In a real system, this would be a more robust messaging system (e.g., message queue, pub/sub)
class AgentCommunicationChannel:
    """
    A placeholder for a communication channel between agents.
    Currently uses a simple in-memory list.
    """
    def __init__(self):
        self._messages: List[AgentMessage] = []

    def send_message(self, message: AgentMessage):
        """Sends a message to the channel."""
        print(f"Sending message from {message.sender_id} to {message.recipient_id} (Type: {message.message_type})")
        self._messages.append(message)

    def get_messages_for_recipient(self, recipient_id: str) -> List[AgentMessage]:
        """Retrieves messages for a specific recipient."""
        # In a real system, messages would be consumed and removed
        recipient_messages = [msg for msg in self._messages if msg.recipient_id == recipient_id]
        # For this simple example, we won't remove them from the list
        return recipient_messages

    def clear_messages(self):
        """Clears all messages in the channel (for testing/cleanup)."""
        self._messages = []

# Example usage (for testing purposes, can be removed later)
if __name__ == "__main__":
    channel = AgentCommunicationChannel()

    msg1 = AgentMessage("AgentA", "AgentB", "task_request", {"task_description": "Analyze data"})
    msg2 = AgentMessage("AgentB", "AgentA", "task_result", {"result": "Analysis complete"}, task_id="task-123")
    msg3 = AgentMessage("AgentA", "AgentC", "feedback", {"comment": "Good job!"}, task_id="task-123")

    channel.send_message(msg1)
    channel.send_message(msg2)
    channel.send_message(msg3)

    print("\nMessages for AgentB:")
    for msg in channel.get_messages_for_recipient("AgentB"):
        print(msg)

    print("\nMessages for AgentA:")
    for msg in channel.get_messages_for_recipient("AgentA"):
        print(msg)

    print("\nMessages for AgentC:")
    for msg in channel.get_messages_for_recipient("AgentC"):
        print(msg)

    channel.clear_messages()
    print(f"\nMessages after clearing: {channel.get_messages_for_recipient('AgentA')}")