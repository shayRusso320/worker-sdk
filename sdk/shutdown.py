"""Graceful shutdown handling for the worker."""

import asyncio
import logging
import signal
import sys
from typing import Callable

logger = logging.getLogger(__name__)


class GracefulShutdownHandler:
    """Manages graceful shutdown on termination signals."""

    def __init__(self, timeout: int) -> None:
        """Initialize shutdown handler.
        
        Args:
            timeout: Graceful shutdown timeout in seconds.
        """
        self.timeout = timeout
        self.shutdown_event = asyncio.Event()
        self._shutdown_callbacks: list[Callable[[], asyncio.Coroutine]] = []

    def register_callback(
        self, callback: Callable[[], asyncio.Coroutine]
    ) -> None:
        """Register a callback to run during shutdown.
        
        Args:
            callback: Async function to call during shutdown.
        """
        self._shutdown_callbacks.append(callback)

    def setup_signal_handlers(self) -> None:
        """Set up signal handlers for SIGTERM and SIGINT.
        
        On Windows, signal handlers work differently than on Unix.
        We use a platform-specific approach.
        """
        if sys.platform == "win32":
            self._setup_windows_signal_handlers()
        else:
            self._setup_unix_signal_handlers()

    def _setup_unix_signal_handlers(self) -> None:
        """Set up signal handlers for Unix-like systems."""
        loop = asyncio.get_event_loop()

        def signal_handler(signum: int, frame: object) -> None:
            logger.info(
                "Received termination signal",
                extra={"signal": signal.Signals(signum).name},
            )
            self.shutdown_event.set()

        loop.add_signal_handler(signal.SIGTERM, signal_handler, signal.SIGTERM, None)
        loop.add_signal_handler(signal.SIGINT, signal_handler, signal.SIGINT, None)

    def _setup_windows_signal_handlers(self) -> None:
        """Set up signal handlers for Windows."""

        def signal_handler(signum: int, frame: object) -> None:
            logger.info(
                "Received termination signal",
                extra={"signal": signal.Signals(signum).name},
            )
            self.shutdown_event.set()

        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

    async def wait_for_shutdown(self) -> None:
        """Wait for shutdown signal and execute callbacks."""
        await self.shutdown_event.wait()
        logger.info("Initiating graceful shutdown")

        try:
            await asyncio.wait_for(
                self._run_callbacks(),
                timeout=self.timeout,
            )
        except asyncio.TimeoutError:
            logger.warning(
                "Graceful shutdown timeout exceeded",
                extra={"timeout": self.timeout},
            )

    async def _run_callbacks(self) -> None:
        """Run all registered shutdown callbacks."""
        for callback in self._shutdown_callbacks:
            try:
                await callback()
            except Exception as e:
                logger.error(
                    "Error during shutdown callback",
                    extra={"error": str(e)},
                    exc_info=True,
                )
