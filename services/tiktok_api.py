"""Thin wrapper for tiktok-scraper7 (RapidAPI).

Documentation: https://rapidapi.com/tikwm-tikwm-default/api/tiktok-scraper7

This module knows nothing about Telegram and how we use it
the result is just executing an HTTP request and returning the parsed JSON."""
import httpx

from config import settings as app_settings


class TikTokAPIError(Exception):
    """Error on the TikTok API side (code != 0 in response)."""


class TikTokScraperClient:
    """Client for the GET /feed/search endpoint of the tiktok-scraper7 service."""

    BASE_URL = "https://tiktok-scraper7.p.rapidapi.com"

    def __init__(
        self,
        api_key: str,
        api_host: str = app_settings.RAPIDAPI_HOST,
        timeout: float = app_settings.HTTP_TIMEOUT,
    ) -> None:
        self._headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": api_host,
        }
        self._client = httpx.AsyncClient(timeout=timeout)

    async def close(self) -> None:
        await self._client.aclose()

    async def search_feed(
        self,
        keywords: str,
        *,
        count: int = 30,
        cursor: int = 0,
        region: str = "",
        publish_time: str = "0",
        sort_type: str = "0",
    ) -> dict:
        """GET /feed/search - search for videos using keywords.

        :param keywords: search query
        :param count: how many videos to return per request (usually up to 30)
        :param cursor: offset for pagination (value from previous answer)
        :param region: ISO 3166-1 alpha-2 country code (e.g. "US"), "" = no filter
        :param publish_time: publication period - "0" all the time, "1" day,
            "7" week, "30" month, "90" 3 months, "180" six months
        :param sort_type: sorting - "0" by relevance, "1" by likes"""
        params: dict[str, str] = {
            "keywords": keywords,
            "count": str(count),
            "cursor": str(cursor),
            "publish_time": str(publish_time),
            "sort_type": str(sort_type),
        }
        if region:
            params["region"] = region

        response = await self._client.get(
            f"{self.BASE_URL}/feed/search",
            headers=self._headers,
            params=params,
        )
        response.raise_for_status()
        payload = response.json()

        if payload.get("code") != 0:
            raise TikTokAPIError(payload.get("msg", "Неизвестная ошибка TikTok API"))

        return payload
