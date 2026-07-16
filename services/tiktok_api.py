"""
Тонкая обёртка над tiktok-scraper7 (RapidAPI).

Документация: https://rapidapi.com/tikwm-tikwm-default/api/tiktok-scraper7

Этот модуль ничего не знает про Telegram и про то, как мы используем
результат — только выполняет HTTP-запрос и отдаёт разобранный JSON.
"""
import httpx

from config import settings as app_settings


class TikTokAPIError(Exception):
    """Ошибка на стороне TikTok API (code != 0 в ответе)."""


class TikTokScraperClient:
    """Клиент для эндпоинта GET /feed/search сервиса tiktok-scraper7."""

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
        """
        GET /feed/search — поиск видео по ключевым словам.

        :param keywords: поисковый запрос
        :param count: сколько видео вернуть за один запрос (обычно до 30)
        :param cursor: смещение для пагинации (значение из предыдущего ответа)
        :param region: код страны ISO 3166-1 alpha-2 (например "US"), "" = без фильтра
        :param publish_time: период публикации — "0" всё время, "1" сутки,
            "7" неделя, "30" месяц, "90" 3 месяца, "180" полгода
        :param sort_type: сортировка — "0" по релевантности, "1" по лайкам
        """
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
