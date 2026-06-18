from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

Role = Literal["system", "user", "assistant", "tool"]

@dataclass
class Message:
    role: Role
    content: str
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self):
        return {"role": self.role, "content": self.content}

    def estimated_tokens(self) -> int:
        return max(1, len(self.content.encode("utf-8")) // 4)

class Session:
    def __init__(self, max_messages=80, token_limit=28000):
        self.messages = []
        self.max_messages = max_messages
        self.token_limit = token_limit

    def add(self, role, content):
        self.messages.append(Message(role=role, content=content))
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def estimated_tokens(self) -> int:
        return sum(m.estimated_tokens() for m in self.messages)

    def prune(self) -> int:
        if self.estimated_tokens() <= self.token_limit:
            return 0

        removed = 0
        new_messages = []
        tool_count = 0

        for msg in self.messages:
            if msg.role == "tool":
                tool_count += 1
                if tool_count <= 10:
                    new_messages.append(msg)
                else:
                    removed += 1
            else:
                new_messages.append(msg)

        if removed > 0:
            self.messages = new_messages

        if self.estimated_tokens() > self.token_limit and len(self.messages) > 10:
            cut = len(self.messages) - 10
            removed += cut
            self.messages = self.messages[-10:]

        return removed

    def to_api_format(self):
        return [m.to_dict() for m in self.messages]

    def clear(self):
        self.messages = []
