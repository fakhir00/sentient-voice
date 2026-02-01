import sys
from loguru import logger
from app.core.config import settings

def setup_logging():
    logger.remove()
    
    # JSON formatting for production/HIPAA audit trails
    logger.add(
        sys.stderr,
        format="{time} | {level} | {message}",
        level="INFO",
        serialize=settings.HIPAA_MODE # JSON logs in HIPAA mode
    )
    
    logger.info("Logging initialized", hipaa_mode=settings.HIPAA_MODE)

# TODO: Add PII sanitization sink
