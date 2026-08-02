"""Downloading binary files (audio) via a direct link."""
from pathlib import Path

import httpx


async def download_file(client: httpx.AsyncClient, url: str, destination: Path) -> Path:
    """Downloads a file from a URL and saves it to the specified path."""
    response = await client.get(url)
    response.raise_for_status()
    destination.write_bytes(response.content)
    return destination
