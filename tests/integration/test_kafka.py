import asyncio
import json
import os
import socket

import pytest

from prompt_autoimprove.config import get_settings
from prompt_autoimprove.services.kafka_producer import EventPublisher, PipelineEvent


def _broker_reachable(addr: str) -> bool:
    host, _, port = addr.partition(":")
    try:
        with socket.create_connection((host, int(port or 9092)), timeout=0.5):
            return True
    except OSError:
        return False


BROKER = os.environ.get("PAI_KAFKA__BOOTSTRAP_SERVERS", "localhost:9092")
pytestmark = pytest.mark.skipif(
    not _broker_reachable(BROKER), reason=f"kafka broker not reachable at {BROKER}"
)


@pytest.mark.asyncio
async def test_publish_and_consume_round_trip() -> None:
    os.environ["PAI_KAFKA__ENABLED"] = "true"
    os.environ["PAI_KAFKA__BOOTSTRAP_SERVERS"] = BROKER
    get_settings.cache_clear()

    from aiokafka import AIOKafkaConsumer

    topic = "pai.events.test"
    publisher = EventPublisher(topic=topic)
    await publisher.start()

    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=BROKER,
        group_id="pai-test",
        auto_offset_reset="earliest",
        enable_auto_commit=False,
    )
    await consumer.start()
    try:
        event = PipelineEvent.now("normalized", "session-xyz", {"task": "summarize"})
        await publisher.publish(event)

        msg = await asyncio.wait_for(consumer.getone(), timeout=10.0)
        body = json.loads(msg.value)
        assert body["stage"] == "normalized"
        assert body["session_id"] == "session-xyz"
        assert body["payload"] == {"task": "summarize"}
        assert msg.key == b"session-xyz"
    finally:
        await publisher.stop()
        await consumer.stop()
        os.environ.pop("PAI_KAFKA__ENABLED", None)
        get_settings.cache_clear()
