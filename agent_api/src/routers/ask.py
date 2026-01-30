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


# @router.get("/stream")
# async def ask_question(prompt:str):
#     ollama_client = get_ollama_client()

#     system_prompt = """
# <SYSTEM>
# Role:
# You are KeyNote AI.

# Identity:
# KeyNote AI is an AI assistant specialized in understanding, summarizing,
# and explaining what happened during events.

# Core Purpose:
# Your primary function is to analyze event-related information and generate
# clear, structured summaries describing what occurred during an event.

# Secondary Function:
# You may respond politely to general, greeting, or identity-related questions,
# but your main focus must always remain on events.


# <REDIRECTION>
# When the input is not event-related, end the response with a short,
# polite prompt encouraging the user to share or ask about an event.
# </REDIRECTION>


# """
#     prompt = prompt = f"""
# {system_prompt}

# <USER_INPUT>
# {prompt}
# </USER_INPUT>
# """


#     health_check = await ollama_client.health_check()
#     print(health_check)
#     async def generate_stream():
#         full_response = ""
#         async for chunk in ollama_client.stream_generate_text(
#             model="gemma3:1b",
#             prompt=prompt,
#         ):
#             if chunk.get("response"):
#                 full_response += chunk["response"]
#                 yield f"data: {json.dumps({'chunk': chunk})}\n\n"
#             if chunk.get("done", False):
#                 yield f"data: {json.dumps({'answer': full_response, 'done': True})}\n\n"
#                 break

#     return StreamingResponse(
#         generate_stream(), media_type="text/plain", headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
#     )

from groq import AsyncGroq

async def response_generator(prompt:str):
    client = AsyncGroq()
    try:
        system_prompt = """
<SYSTEM>
Role:
You are KeyNote AI.

Identity:
KeyNote AI is an AI assistant specialized in understanding, summarizing,
and explaining what happened during events.

Core Purpose:
Your primary function is to analyze event-related information and generate
clear, structured summaries describing what occurred during an event.

Secondary Function:
You may respond politely to general, greeting, or identity-related questions,
but your main focus must always remain on events.


<REDIRECTION>
When the input is not event-related, end the response with a short,
polite prompt encouraging the user to share or ask about an event.
</REDIRECTION>


"""
        prompt = prompt = f"""
{system_prompt}

<USER_INPUT>
{prompt}
</USER_INPUT>
"""
        stream = await client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="openai/gpt-oss-120b",
            stream=True, #
        )

        # Iterate over the stream asynchronously
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                # Yield the content chunk directly
                yield content
                
                
    except Exception as e:
        yield f"Error: {str(e)}"

@router.post("/stream")
async def stream_chat(prompt:str):
    """
    Endpoint to stream responses from Groq.
    """

    # Return a StreamingResponse
    # media_type="text/event-stream" is standard for Server-Sent Events (SSE)
    return StreamingResponse(
        response_generator(prompt),
        media_type="text/event-stream"
    )
