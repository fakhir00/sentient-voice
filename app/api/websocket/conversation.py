from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger
from app.voice_engine.pipeline import VoicePipeline

router = APIRouter()

@router.websocket("/conversation")
async def websocket_endpoint(websocket: WebSocket):
    print("🔥 WEBSOCKET HIT: Connection attempt received!")
    await websocket.accept()
    logger.info("WebSocket connection accepted")
    
    pipeline = VoicePipeline() 
    # In future phases: pipeline.workers = [Transcriber(), Agent(), Synthesizer(), Output(websocket)]
    
    try:
        await pipeline.start()
        
        while True:
            data = await websocket.receive_bytes()
            # Feed audio to the pipeline
            await pipeline.process_audio_chunk(data)
            
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.exception(f"WebSocket error: {e}")
    finally:
        await pipeline.terminate()
        logger.info("Pipeline terminated")
