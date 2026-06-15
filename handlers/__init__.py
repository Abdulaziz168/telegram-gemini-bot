"""Handlers package for bot message routing."""
from .message_handler import router as message_router
from .voice_handler import router as voice_router
from .features_handler import router as features_router
from .admin_handler import router as admin_router

__all__ = ['message_router', 'voice_router', 'features_router', 'admin_router']
