"""Agent-facing wrapper for the C tool server transport."""

from dataclasses import dataclass

from ai_assistant.tools.protobuf import SerializableProto
from ai_assistant.tools.unix_socket_client import UnixSocketProtobufClient


@dataclass(frozen=True, slots=True)
class ToolSocketAgent:
    client: UnixSocketProtobufClient

    def submit(self, request: SerializableProto) -> bytes:
        return self.client.request(request)

