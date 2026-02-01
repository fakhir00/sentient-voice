import asyncio
import json
from loguru import logger
from deepgram import DeepgramClient

# Try importing EventType, fallback to string literals if needed
try:
    from deepgram.core.events import EventType
    EVENT_MESSAGE = EventType.MESSAGE
    EVENT_ERROR = EventType.ERROR
except ImportError:
    EVENT_MESSAGE = "message"
    EVENT_ERROR = "error"

from app.core.config import settings
from app.voice_engine.primitive.worker import BaseWorker
from app.voice_engine.primitive.events import TranscriptEvent

class DeepgramTranscriber(BaseWorker):
    def __init__(self, input_queue: asyncio.Queue, output_queue: asyncio.Queue):
        super().__init__(input_queue, output_queue)
        # Initialize client without options first
        self.dg_client = DeepgramClient(api_key=settings.DEEPGRAM_API_KEY)

    async def _run_loop(self):
        # Configure Options via kwargs
        options = {
            "model": "nova-2",
            "language": "en-US",
            "smart_format": True,
            "interim_results": True,
        }

        # Events
        async def on_message(self_handler, result, **kwargs):
             # Deepgram SDK v3+ returns an object, not dict
             # Use safe access or check type
             # result might be ListenV1ResultsEvent type
             
             # The result structure usually matches the JSON response
             # e.g. result.channel.alternatives[0].transcript
             
             try:
                 # Check if it has 'channel' attribute (Result Event)
                 if hasattr(result, 'channel'):
                     alternatives = result.channel.alternatives
                     if alternatives and len(alternatives) > 0:
                         sentence = alternatives[0].transcript
                         if len(sentence) == 0:
                             return
                             
                         is_final = result.is_final
                         confidence = alternatives[0].confidence
                         
                         event = TranscriptEvent(
                             text=sentence,
                             is_final=is_final,
                             confidence=confidence
                         )
                         
                         if self.output_queue:
                             await self.output_queue.put(event)
                         
                         logger.debug(f"Transcript: {sentence} (Final: {is_final})")
             except Exception as e:
                 logger.error(f"Error processing transcript: {e}")

        async def on_error(self_handler, error, **kwargs):
            logger.error(f"Deepgram Error: {error}")

        logger.info("Deepgram Transcriber Started")
        
        try:
            # Connect using the new pattern
            async with self.dg_client.listen.asyncwebsocket.v("1").connect(**options) as socket:
                
                # Register handlers
                socket.on(EVENT_MESSAGE, on_message)
                socket.on(EVENT_ERROR, on_error)
                
                # Send Audio Loop
                while self.active:
                    chunk = await self.input_queue.get()
                    if chunk is None:
                        break
                        
                    await socket.send(chunk)
                    self.input_queue.task_done()
                    
        except Exception as e:
            logger.exception(f"Transcriber Loop Error: {e}")
        finally:
            logger.info("Deepgram Transcriber Stopped")
