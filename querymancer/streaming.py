import json
from typing import Generator

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from querymancer.agent import create_history, ask_stream
from querymancer.config import Config
from querymancer.models import create_llm


router = APIRouter()

llm = create_llm(Config.MODEL)


def sse_event(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


@router.get("/api/query/stream")
def query_stream(query: str = Query(..., min_length=1)):

    def event_generator() -> Generator[str, None, None]:

        try:

            history = create_history()

            for event in ask_stream(
                query=query,
                history=history,
                llm=llm,
            ):
                yield sse_event(event)

            yield sse_event({
                "type": "done"
            })

        except Exception as e:

            yield sse_event({
                "type": "error",
                "message": str(e),
            })

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )