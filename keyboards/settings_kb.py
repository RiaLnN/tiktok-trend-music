"""Inline keyboards for the /settings menu."""
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.callback_data import SettingsCB
from models.settings import PUBLISH_TIME_LABELS, REGIONS, SORT_TYPE_LABELS, UserSettings
from utils.constants import TRACK_COUNT_OPTIONS, VIDEOS_PER_TRACK_OPTIONS


def main_menu_kb(s: UserSettings) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=f"🔑 Ключевые слова ({len(s.keywords)})", callback_data=SettingsCB(action="keywords"))
    builder.button(text=f"🌍 Страна: {REGIONS.get(s.region, s.region or '—')}", callback_data=SettingsCB(action="region"))
    builder.button(text=f"🕒 Период: {PUBLISH_TIME_LABELS[s.publish_time]}", callback_data=SettingsCB(action="period"))
    builder.button(text=f"📊 Сортировка: {SORT_TYPE_LABELS[s.sort_type]}", callback_data=SettingsCB(action="sort"))
    builder.button(text=f"🔢 Треков за раз: {s.tracks_count}", callback_data=SettingsCB(action="count"))
    builder.button(text=f"🎬 Видео на трек: {s.videos_per_track}", callback_data=SettingsCB(action="videos"))
    builder.button(text="✅ Готово", callback_data=SettingsCB(action="close"))
    builder.adjust(1)
    return builder.as_markup()


def keywords_kb(keywords: list[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for kw in keywords:
        builder.button(text=f"❌ {kw}", callback_data=SettingsCB(action="remove_keyword", value=kw))
    builder.button(text="➕ Добавить ключевое слово", callback_data=SettingsCB(action="add_keyword"))
    builder.button(text="⬅️ Назад", callback_data=SettingsCB(action="menu"))
    builder.adjust(1)
    return builder.as_markup()


def region_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for code, label in REGIONS.items():
        builder.button(text=label, callback_data=SettingsCB(action="set_region", value=code))
    builder.button(text="⬅️ Назад", callback_data=SettingsCB(action="menu"))
    builder.adjust(2)
    return builder.as_markup()


def period_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for value, label in PUBLISH_TIME_LABELS.items():
        builder.button(text=label, callback_data=SettingsCB(action="set_period", value=value.value))
    builder.button(text="⬅️ Назад", callback_data=SettingsCB(action="menu"))
    builder.adjust(1)
    return builder.as_markup()


def sort_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for value, label in SORT_TYPE_LABELS.items():
        builder.button(text=label, callback_data=SettingsCB(action="set_sort", value=value.value))
    builder.button(text="⬅️ Назад", callback_data=SettingsCB(action="menu"))
    builder.adjust(1)
    return builder.as_markup()


def count_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for n in TRACK_COUNT_OPTIONS:
        builder.button(text=str(n), callback_data=SettingsCB(action="set_count", value=str(n)))
    builder.button(text="⬅️ Назад", callback_data=SettingsCB(action="menu"))
    builder.adjust(len(TRACK_COUNT_OPTIONS))
    return builder.as_markup()


def videos_per_track_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for n in VIDEOS_PER_TRACK_OPTIONS:
        builder.button(text=str(n), callback_data=SettingsCB(action="set_videos", value=str(n)))
    builder.button(text="⬅️ Назад", callback_data=SettingsCB(action="menu"))
    builder.adjust(len(VIDEOS_PER_TRACK_OPTIONS))
    return builder.as_markup()
