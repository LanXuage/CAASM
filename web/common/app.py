#!/bin/env python
from typing import Set
from fastapi import FastAPI
from redis.asyncio import Redis
from captcha.image import ImageCaptcha
from cryptography.fernet import Fernet
from nebula3.gclient.net.SessionPool import SessionPool


class App(FastAPI):
    token_fernet: Fernet
    invalid_tokens: Set[str]
    token_ttl: int
    image_captcha: ImageCaptcha
    redis: Redis
    nebula_sess_pool: SessionPool
