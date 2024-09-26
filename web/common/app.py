#!/bin/env python3
from typing import Set
from fastapi import FastAPI
from redis.asyncio import Redis
from captcha.image import ImageCaptcha
from cryptography.fernet import Fernet
from .nebula import NebulaFacade
from .queue import NotifyQueue, TaskQueue
from .websocket import WebSocketManager
from .file import FileManager


class App(FastAPI):
    token_fernet: Fernet
    invalid_tokens: Set[str]
    token_ttl: int
    image_captcha: ImageCaptcha
    redis: Redis
    nebula_facade: NebulaFacade
    websocket_manager: WebSocketManager
    notify_queue: NotifyQueue
    task_queue: TaskQueue
    file_manager: FileManager
