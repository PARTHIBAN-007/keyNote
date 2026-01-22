from fastapi import APIRouter
from fastapi.responses import StreamingResponse

import json
from src.services.ollama.factory import get_ollama_client

router = APIRouter(
    tags=["ask"]
)

@router.get("/ask")
async def ask_question(prompt:str):
    ollama_client = get_ollama_client()

    health_check = await ollama_client.health_check()
    print(health_check)

    response = await ollama_client.generate_text(
        model="gemma3:1b",
        prompt=prompt,
        stream=False
    )

    return response


@router.get("/stream")
async def ask_question(prompt:str):
    ollama_client = get_ollama_client()

    health_check = await ollama_client.health_check()
    print(health_check)
    async def generate_stream():
        full_response = ""
        async for chunk in ollama_client.stream_generate_text(
            model="gemma3:1b",
            prompt=prompt,
        ):
            if chunk.get("response"):
                full_response += chunk["response"]
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            if chunk.get("done", False):
                yield f"data: {json.dumps({'answer': full_response, 'done': True})}\n\n"
                break

    return StreamingResponse(
        generate_stream(), media_type="text/plain", headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )
