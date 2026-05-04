import httpx
import pytest


@pytest.mark.asyncio
async def test_sse_stream_emits_pipeline_stages(client: httpx.AsyncClient) -> None:
    headers = {"x-api-key": "test-key", "accept": "text/event-stream"}
    params = {"prompt": "Summarize this article", "profile": "qwen3-7b"}
    seen_events: list[str] = []
    async with client.stream("GET", "/v1/improve/stream", headers=headers, params=params) as resp:
        assert resp.status_code == 200
        async for line in resp.aiter_lines():
            if line.startswith("event:"):
                seen_events.append(line.removeprefix("event:").strip())
                if "final_decision" in seen_events:
                    break
    assert seen_events[0] == "normalized"
    assert "strategy_selected" in seen_events
    assert "candidate" in seen_events
    assert "evaluated" in seen_events
    assert seen_events[-1] == "final_decision"
