#!/bin/env python3
import asyncio

from threading import Lock
from .queue import NotifyQueue
from fastapi import WebSocket
from typing import Dict, Any, Optional


class WebSocketManager:
    notify_consumer: Optional[asyncio.Task] = None
    lock = Lock()

    def __init__(self, notify_queue: NotifyQueue) -> None:
        self.websockets: Dict[str, WebSocket] = {}
        self.notify_queue = notify_queue

    async def add_websocket(self, key: Any, web_socket: WebSocket):
        self.websockets[key] = web_socket
        if self.notify_consumer is None or self.notify_consumer.done():
            with WebSocketManager.lock:
                if self.notify_consumer is None or self.notify_consumer.done():
                    self.notify_consumer = asyncio.get_running_loop().create_task(
                        self.notify_consumer_loop()
                    )

    async def process_event(self, event: dict, username: Any):
        t = event.get("type")
        if t == "close":
            await self.close_websocket(username)

    async def notify_consumer_loop(self):
        while True:
            pass

    async def close_websocket(self, username: Any):
        websocket = self.websockets.get(username)
        if websocket is not None:
            del self.websockets[username]
            await websocket.close()

    async def close(self):
        for web_socket in self.websockets.values():
            try:
                await web_socket.close()
            except:
                pass
