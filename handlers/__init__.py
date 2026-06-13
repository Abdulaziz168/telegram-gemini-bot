"""Handlers package for bot message routing."""
from .message_handler import router as message_router
from .voice_handler import router as voice_router

__all__ = ['message_router', 'voice_router']
