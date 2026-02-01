from typing import Optional
from pydantic import BaseModel

class TranscriptEvent(BaseModel):
    text: str
    is_final: bool
    confidence: float = 1.0

class LLMChunkEvent(BaseModel):
    token: str
    
class AudioChunkEvent(BaseModel):
    chunk: bytes
