import re
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger

class LogRedactorMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        # Regex patterns for PII
        self.ssn_pattern = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})\b')

    def redact(self, text: str) -> str:
        """Redacts PII from text."""
        if not text:
            return text
            
        # Mask SSN
        text = self.ssn_pattern.sub('XXX-XX-XXXX', text)
        
        # Mask Email
        text = self.email_pattern.sub('[REDACTED_EMAIL]', text)
        
        # Mask Phone (keep last 4)
        def mask_phone(match):
            return f"XXX-XXX-{match.group(3)}"
        text = self.phone_pattern.sub(mask_phone, text)
        
        return text

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # We can't easily read the request body without consuming it, 
        # so we primarily log the URL and method here.
        # Use a binding to ensure redaction in context if needed.
        
        url_path = self.redact(str(request.url))
        logger.info(f"Incoming Request: {request.method} {url_path}")
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        logger.info(f"Request completed: {request.method} {url_path} - Status: {response.status_code} - Duration: {process_time:.4f}s")
        
        return response
