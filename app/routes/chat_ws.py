import json
import asyncio
from collections import defaultdict
from typing import List, Tuple

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.services.nlp_service import generate_response

router = APIRouter()

# In-memory per-connection history: connection ID → [(role, message), ...]
CONN_HISTORY: defaultdict[int, List[Tuple[str, str]]] = defaultdict(list)

@router.websocket("/chat/ws")
async def chat_ws(
    websocket: WebSocket,
    model: str = Query(
        "transformer",
        description="Which model to use: 'ml' or 'transformer'",
        enum=["ml", "transformer"]
    )
):
    """
    WebSocket endpoint for streaming chat responses.
    Sends typing indicators and streams sentences back to the client.
    """
    await websocket.accept()
    conn_id = id(websocket)
    history = CONN_HISTORY[conn_id]

    try:
        while True:
            # Receive a JSON payload: {"message": "..."}
            data = await websocket.receive_text()
            payload = json.loads(data)
            user_msg = payload.get("message", "").strip()

            # Basic validation
            if not user_msg:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Empty message, please send a non-empty string."
                }))
                continue

            # Record user turn
            history.append(("user", user_msg))

            # Send typing indicator
            await websocket.send_text(json.dumps({"type": "typing"}))

            # Generate full response using existing NLU logic
            full_reply = await generate_response(
                message=user_msg,
                model_type=model,
                context=history
            )

            # Stream the reply in sentence chunks
            sentences = [s + ("." if not s.endswith(".") else "") for s in full_reply.rstrip().split(".") if s]
            for sent in sentences:
                await websocket.send_text(json.dumps({
                    "type": "message",
                    "content": sent + " "
                }))
                # slight pause to simulate streaming
                await asyncio.sleep(0.05)

            # Record bot turn
            history.append(("bot", full_reply))

            # Signal end of streaming
            await websocket.send_text(json.dumps({"type": "done"}))

    except WebSocketDisconnect:
        # Clean up per-connection history
        CONN_HISTORY.pop(conn_id, None)
