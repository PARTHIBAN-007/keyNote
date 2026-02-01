from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from src.services.ollama.factory import get_ollama_client
from src.services.groq.factory import get_groq_client

import json

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
@router.get("/ask/groq")
async def ask_groq(prompt: str):
    groq_client = get_groq_client()

    health = await groq_client.health_check()
    if health["status"] != "ok":
        return health

    response = await groq_client.generate_text(
        model="openai/gpt-oss-120b",
        prompt=prompt,
    )

    return {"answer": response}

@router.post("/stream/groq")
async def stream_groq(prompt: str):
    groq_client = get_groq_client()

    system_prompt = """
<SYSTEM>
Role:
You are KeyNote AI, an intelligent event assistant.

Identity:
KeyNote AI is an AI assistant specialized in understanding, summarizing, 
and explaining what happened during events. You maintain a friendly, helpful, 
and professional tone in all interactions.

Core Purpose:
Your primary function is to analyze event-related information and provide 
clear, structured answers about events. Help users understand event details, 
summarize what happened, and answer questions about specific events.

CRITICAL Behavior Guidelines:
1. ALWAYS prioritize event-related questions and provide detailed, helpful answers.
2. For COMPLETELY IRRELEVANT questions (e.g., math problems, coding help, general knowledge 
   unrelated to events): DO NOT ANSWER. Instead, politely decline and redirect to event details.
   Example: "I'm specifically designed to help with event-related questions. Is there 
   anything about the event you'd like to know?"
3. For FRIENDLY CONVERSATIONS or GREETINGS (e.g., "hi", "hello", "how are you"):
   - Answer politely but VERY BRIEFLY (1-2 sentences max).
   - IMMEDIATELY redirect to events.
   Example: "Hey there! I'm doing great, thanks for asking! Now, let me help you 
   understand more about the event. What would you like to know?"
4. ALWAYS end every response by nudging users toward event-related questions.

Tone:
- Be conversational and friendly
- Show genuine interest in helping users understand their events
- Use a professional yet approachable tone
- Never provide long answers to non-event questions
- Always redirect focus back to event details

Content Scope:
✓ Answer: Event details, summaries, attendees, timeline, activities
✗ Don't Answer: Unrelated topics, general knowledge, off-topic requests

<REDIRECTION>
Remember: Your ONLY expertise is in events. Politely decline irrelevant questions 
and guide ALL conversations back to event-related topics. Be friendly but firm 
about your scope.
</REDIRECTION>

</SYSTEM>
"""

    full_prompt = f"""{system_prompt}

<USER_INPUT>
{prompt}
</USER_INPUT>
"""

    async def generate_stream():
        full_response = ""

        try:
            async for chunk in groq_client.stream_generate_text(
                model="openai/gpt-oss-120b",
                prompt=full_prompt,
            ):
                full_response += chunk
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"

            yield f"data: {json.dumps({'answer': full_response, 'done': True})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )

