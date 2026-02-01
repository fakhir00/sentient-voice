# Fully implemented Pipeline
import asyncio
from typing import List

from app.voice_engine.primitive.worker import BaseWorker
from app.voice_engine.workers.transcriber import DeepgramTranscriber
from app.voice_engine.workers.llm import GroqLLMWorker
# from app.voice_engine.workers.synthesizer import ElevenLabsSynthesizer # Commented out until valid API key usage

class VoicePipeline:
    """
    Orchestrates the lifecycle of the voice workers (Transcriber -> Agent -> Synthesizer -> Output).
    """
    def __init__(self):
        # Queues
        self.audio_input_queue = asyncio.Queue()
        self.transcription_queue = asyncio.Queue()
        self.agent_input_queue = asyncio.Queue() # Same as transcription_queue usually, but separation allows middleware
        self.synthesis_input_queue = asyncio.Queue()
        self.audio_output_queue = asyncio.Queue()
        
        # Instantiate Workers
        # 1. Transcriber: Audio In -> Transcription Out
        self.transcriber = DeepgramTranscriber(
            input_queue=self.audio_input_queue,
            output_queue=self.transcription_queue
        )
        
        # 2. LLM: Transcription In (as Agent Input) -> Text Chunk Out (to Synthesis)
        self.llm = GroqLLMWorker(
            input_queue=self.transcription_queue,
            output_queue=self.synthesis_input_queue
        )
        
        # 3. Synthesizer: Text Chunk In -> Audio Out
        # self.synthesizer = ElevenLabsSynthesizer(
        #     input_queue=self.synthesis_input_queue,
        #     output_queue=self.audio_output_queue
        # )
        
        self.workers: List[BaseWorker] = [
            self.transcriber,
            self.llm,
            # self.synthesizer
        ]

    async def start(self):
        # Start all workers
        for worker in self.workers:
            worker.start()

    async def terminate(self):
        # Stop all workers
        for worker in self.workers:
            await worker.terminate()

    async def process_audio_chunk(self, chunk: bytes):
        """Entry point for audio from WebSocket"""
        await self.audio_input_queue.put(chunk)

