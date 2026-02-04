from groq import AsyncGroq
from typing import AsyncGenerator, Optional


class GroqClient:
    def __init__(self, api_key: Optional[str] = None):
        self.client = AsyncGroq(api_key=api_key)

    async def health_check(self) -> dict:
        """
        Groq does not provide a native health endpoint.
        Perform a minimal request to verify connectivity.
        """
        try:
            await self.client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=1,
            )
            return {"status": "ok"}
        except Exception as e:
            return {"status": "error", "detail": str(e)}

    async def generate_text(
        self,
        model: str,
        prompt: str,
    ) -> str:
        """
        Non-streaming text generation.
        """
        response = await self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            stream=False,
        )

        return response.choices[0].message.content

    async def stream_generate_text(
        self,
        model: str,
        prompt: str,
    ) -> AsyncGenerator[str, None]:
        """
        Streaming text generation.
        Yields text chunks as they arrive.
        """
        stream = await self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            stream=True,
        )

        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content
