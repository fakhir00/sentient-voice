import asyncio
import logging
from typing import Optional, Any, Generic, TypeVar

T = TypeVar("T")

logger = logging.getLogger(__name__)

class InterruptibleEvent(Generic[T]):
    """
    Wrapper for payloads that can be interrupted.
    Used to propagate interruption signals through the pipeline.
    """
    def __init__(self, payload: T, is_interruptible: bool = True):
        self.payload = payload
        self.is_interruptible = is_interruptible
        self.interruption_event = asyncio.Event()
        self.interrupted = False

    def interrupt(self) -> bool:
        """
        Signal that this event should be interrupted.
        Returns True if newly interrupted, False if already interrupted or not interruptible.
        """
        if not self.is_interruptible:
            return False
        
        if not self.interrupted:
            self.interruption_event.set()
            self.interrupted = True
            return True
        return False

    def is_set(self) -> bool:
        return self.interruption_event.is_set()


class BaseWorker:
    """
    Base class for all pipeline workers.
    Consumes from input_queue processing items and optionally putting to output_queue.
    """
    def __init__(self, input_queue: asyncio.Queue, output_queue: Optional[asyncio.Queue] = None):
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.active = False
        self.task: Optional[asyncio.Task] = None

    def start(self):
        """Start the worker's processing loop."""
        if not self.active:
            self.active = True
            self.task = asyncio.create_task(self._run_loop())
            logger.info(f"{self.__class__.__name__} started")

    async def _run_loop(self):
        """Main loop: consumes items from queue and processes them."""
        while self.active:
            try:
                item = await self.input_queue.get()
                if item is None: # Sentinel for shutdown
                    break
                
                await self.process(item)
                self.input_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception(f"Error in {self.__class__.__name__}: {e}")

    async def process(self, item: Any):
        """Override this method to implement worker logic."""
        raise NotImplementedError

    async def terminate(self):
        """Stop the worker gracefully."""
        self.active = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info(f"{self.__class__.__name__} terminated")
