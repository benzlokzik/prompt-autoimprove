import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any

from prompt_autoimprove.config import get_settings
from prompt_autoimprove.logging import get_logger

logger = get_logger(__name__)


@dataclass(slots=True, frozen=True)
class PipelineEvent:
    stage: str
    session_id: str
    payload: dict[str, Any]
    occurred_at: str

    @classmethod
    def now(cls, stage: str, session_id: str, payload: dict[str, Any]) -> "PipelineEvent":
        return cls(
            stage=stage,
            session_id=session_id,
            payload=payload,
            occurred_at=datetime.now(UTC).isoformat(),
        )


class EventPublisher:
    def __init__(self, topic: str = "pai.events") -> None:
        self.topic = topic
        self._producer: Any = None
        self._enabled = get_settings().kafka.enabled

    async def start(self) -> None:
        if not self._enabled:
            return
        from aiokafka import AIOKafkaProducer

        settings = get_settings().kafka
        self._producer = AIOKafkaProducer(
            bootstrap_servers=settings.bootstrap_servers,
            client_id=settings.client_id,
        )
        await self._producer.start()

    async def stop(self) -> None:
        if self._producer is not None:
            await self._producer.stop()
            self._producer = None

    async def publish(self, event: PipelineEvent) -> None:
        body = json.dumps(asdict(event)).encode()
        if self._producer is None:
            logger.info("event.skipped", stage=event.stage, session_id=event.session_id)
            return
        await self._producer.send_and_wait(self.topic, body, key=event.session_id.encode())
