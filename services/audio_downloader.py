"""Скачивание бинарных файлов (аудио) по прямой ссылке."""
from pathlib import Path

import httpx


async def download_file(client: httpx.AsyncClient, url: str, destination: Path) -> Path:
    """Скачивает файл по url и сохраняет его по указанному пути."""
    response = await client.get(url)
    response.raise_for_status()
    destination.write_bytes(response.content)
    return destination
