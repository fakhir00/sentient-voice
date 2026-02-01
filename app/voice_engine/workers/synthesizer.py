import asyncio
import websockets
import json
import base64
from loguru import logger

from app.core.config import settings
from app.voice_engine.primitive.worker import BaseWorker
from app.voice_engine.primitive.events import LLMChunkEvent, AudioChunkEvent

class ElevenLabsSynthesizer(BaseWorker):
    def __init__(self, input_queue: asyncio.Queue, output_queue: asyncio.Queue):
        super().__init__(input_queue, output_queue)
        self.voice_id = "21m00Tcm4TlvDq8ikWAM" # Default: Rachel. Replace with Dental Receptionist ID later.
        self.model_id = "eleven_turbo_v2_5"
        self.ws_url = f"wss://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}/stream-input?model_id={self.model_id}"

    async def _run_loop(self):
        logger.info("ElevenLabs Synthesizer Started")
        
        async with websockets.connect(self.ws_url) as ws:
            # Send initial config (BOS)
            bos_message = {
                "text": " ",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.8},
                "xi_api_key": settings.ELEVENLABS_API_KEY,
            }
            await ws.send(json.dumps(bos_message))

            # Task 1: Receiver (Audio from ElevenLabs)
            rx_task = asyncio.create_task(self._receiver(ws))
            
            # Task 2: Sender (Text to ElevenLabs)
            try:
                while self.active:
                    item = await self.input_queue.get()
                    if item is None:
                        break
                    
                    if isinstance(item, LLMChunkEvent):
                        # Send text chunk
                        payload = {"text": item.token, "try_trigger_generation": True}
                        await ws.send(json.dumps(payload))
                    
                    self.input_queue.task_done()
                
                # Send EOS
                await ws.send(json.dumps({"text": ""}))

            except Exception as e:
                logger.exception(f"Synthesizer Sender Error: {e}")
            finally:
                await rx_task

    async def _receiver(self, ws):
        try:
            while True:
                response = await ws.recv()
                data = json.loads(response)
                
                if data.get("audio"):
                    chunk = base64.b64decode(data["audio"])
                    if self.output_queue:
                         await self.output_queue.put(AudioChunkEvent(chunk=chunk))
                
                if data.get("isFinal"):
                    break
        except websockets.exceptions.ConnectionClosed:
            logger.info("ElevenLabs Connection Closed")
        except Exception as e:
            logger.exception(f"Synthesizer Receiver Error: {e}")
