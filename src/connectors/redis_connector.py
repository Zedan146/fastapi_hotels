import logging

import redis.asyncio as redis


class RedisManager:
    def __init__(self, host: str, port: int, password: str):
        self.host = host
        self.port = port
        self.password = password
        self.redis = None

    async def connector(self):
        """Устанавливает асинхронное подключение к Redis."""
        logging.info(f"Подключение к Redis host={self.host}, port={self.port}")
        self.redis = await redis.Redis(host=self.host, port=self.port, password=self.password)
        logging.info(f"Успешное подключение к Redis host={self.host}, port={self.port}")

    async def set(self, key: str, value: str, expire: int = None):
        """Сохраняет значение в Redis с возможностью указания времени экспирации"""
        if expire:
            await self.redis.set(key, value, ex=expire)
        else:
            await self.redis.set(key, value)

    async def get(self, key: str):
        """Получаем значение по ключу"""
        return await self.redis.get(key)

    async def delete(self, key: str):
        """Удаляем значение по ключу"""
        await self.redis.delete(key)

    async def close(self):
        """Закрывает подключение к Redis"""
        if self.redis:
            await self.redis.close()
