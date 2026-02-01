import asyncio
from typing import List, Dict
from loguru import logger
from groq import AsyncGroq

from app.core.config import settings
from app.voice_engine.primitive.worker import BaseWorker
from app.voice_engine.primitive.events import TranscriptEvent, LLMChunkEvent

class GroqLLMWorker(BaseWorker):
    def __init__(self, input_queue: asyncio.Queue, output_queue: asyncio.Queue):
        super().__init__(input_queue, output_queue)
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.conversation_history: List[Dict[str, str]] = [
            {"role": "system", "content": "You are a helpful dental receptionist named Sarah. Keep answers brief and conversational. Do not use emojis."}
        ]

    async def process(self, item: TranscriptEvent):
        # We only want to process Final transcripts for logic
        # Interim transcripts could be used for advanced "speech-while-thinking" logic later (backchanneling)
        if not item.is_final:
            return

        user_text = item.text
        logger.info(f"User: {user_text}")
        
        # Append User Input
        self.conversation_history.append({"role": "user", "content": user_text})

        # Call Groq
        try:
            stream = await self.client.chat.completions.create(
                messages=self.conversation_history,
                model="llama3-70b-8192",
                stream=True,
                temperature=0.7,
                max_tokens=256
            )

            full_response = ""
            async for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    # Stream chunk to Synthesizer
                    if self.output_queue:
                         await self.output_queue.put(LLMChunkEvent(token=content))

            # Append Assistant Response (for history)
            self.conversation_history.append({"role": "assistant", "content": full_response})
            logger.info(f"Bot: {full_response}")

        except Exception as e:
            logger.exception(f"LLM Error: {e}")
            # Fallback (optional)
            if self.output_queue:
                 await self.output_queue.put(LLMChunkEvent(token="I am having trouble connecting right now."))
