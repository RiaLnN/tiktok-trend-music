"""/settings command handlers.

The menu is built like a tree of inline keyboards: main menu -> submenu
specific parameter -> select a value -> again the main menu.
All transitions use edit_text/edit_reply_markup so as not to overwhelm
Chat with new messages with every click."""
import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards.callback_data import SettingsCB
from keyboards.settings_kb import (
    count_kb,
    keywords_kb,
    main_menu_kb,
    period_kb,
    region_kb,
    sort_kb,
    videos_per_track_kb,
)
from models.settings import PublishTime, SortType, UserSettings
from states.settings_states import SettingsStates
from storage.settings_repository import SettingsRepository
from utils.constants import MAX_KEYWORD_LENGTH

logger = logging.getLogger(__name__)
router = Router(name="settings")


def _summary_text(s: UserSettings) -> str:
    keywords = ", ".join(s.keywords) if s.keywords else "не заданы"
    return (
        "⚙️ <b>Настройки поиска трендов</b>\n\n"
        "Здесь можно настроить, какие треки будет искать бот.\n"
        f"Текущие ключевые слова: <i>{keywords}</i>"
    )


@router.message(Command("settings"))
async def cmd_settings(message: Message, repo: SettingsRepository) -> None:
    user_settings = await repo.get(message.from_user.id) # type: ignore
    await message.answer(_summary_text(user_settings), reply_markup=main_menu_kb(user_settings))


@router.callback_query(SettingsCB.filter(F.action == "menu"))
async def cb_main_menu(callback: CallbackQuery, repo: SettingsRepository) -> None:
    user_settings = await repo.get(callback.from_user.id)
    await callback.message.edit_text(_summary_text(user_settings), reply_markup=main_menu_kb(user_settings)) # type: ignore
    await callback.answer()


@router.callback_query(SettingsCB.filter(F.action == "close"))
async def cb_close(callback: CallbackQuery) -> None:
    await callback.message.edit_text("Настройки сохранены ✅\nЗапустить поиск: /trends") # type: ignore
    await callback.answer()


# --- Keywords ---------------------------------------------------------

@router.callback_query(SettingsCB.filter(F.action == "keywords"))
async def cb_keywords(callback: CallbackQuery, repo: SettingsRepository) -> None:
    user_settings = await repo.get(callback.from_user.id)
    await callback.message.edit_text( # type: ignore
        "🔑 <b>Ключевые слова</b>\n"
        "Бот ищет треки отдельно по каждому слову и объединяет результат в один список.\n"
        "Нажмите на слово, чтобы удалить его.",
        reply_markup=keywords_kb(user_settings.keywords),
    )
    await callback.answer()


@router.callback_query(SettingsCB.filter(F.action == "remove_keyword"))
async def cb_remove_keyword(callback: CallbackQuery, callback_data: SettingsCB, repo: SettingsRepository) -> None:
    user_settings = await repo.get(callback.from_user.id)
    if len(user_settings.keywords) <= 1:
        await callback.answer("Должно остаться хотя бы одно ключевое слово", show_alert=True)
        return

    user_settings.keywords = [kw for kw in user_settings.keywords if kw != callback_data.value]
    await repo.save(callback.from_user.id, user_settings)
    await callback.message.edit_reply_markup(reply_markup=keywords_kb(user_settings.keywords)) # type: ignore
    await callback.answer("Удалено")


@router.callback_query(SettingsCB.filter(F.action == "add_keyword"))
async def cb_add_keyword(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(SettingsStates.waiting_for_keyword)
    await callback.message.edit_text( # type: ignore
        "Введите новое ключевое слово или фразу для поиска "
        f"(например, <i>edit</i> или <i>dota 2</i>, до {MAX_KEYWORD_LENGTH} символов):",
    )
    await callback.answer()


@router.message(SettingsStates.waiting_for_keyword)
async def process_new_keyword(message: Message, state: FSMContext, repo: SettingsRepository) -> None:
    keyword = (message.text or "").strip()
    if not keyword:
        await message.answer("Ключевое слово не может быть пустым. Попробуйте ещё раз:")
        return
    if len(keyword) > MAX_KEYWORD_LENGTH:
        await message.answer(f"Слишком длинно — до {MAX_KEYWORD_LENGTH} символов. Попробуйте короче:")
        return

    user_settings = await repo.get(message.from_user.id) # type: ignore
    if keyword.lower() not in [kw.lower() for kw in user_settings.keywords]:
        user_settings.keywords.append(keyword)
        await repo.save(message.from_user.id, user_settings) # type: ignore

    await state.clear()
    await message.answer(f"Добавлено: <b>{keyword}</b>")
    await message.answer(_summary_text(user_settings), reply_markup=main_menu_kb(user_settings))


# --- Page -------------------------------------------------------------------

@router.callback_query(SettingsCB.filter(F.action == "region"))
async def cb_region(callback: CallbackQuery) -> None:
    await callback.message.edit_text("🌍 Выберите страну, тренды которой будем отслеживать:", reply_markup=region_kb()) # type: ignore
    await callback.answer()


@router.callback_query(SettingsCB.filter(F.action == "set_region"))
async def cb_set_region(callback: CallbackQuery, callback_data: SettingsCB, repo: SettingsRepository) -> None:
    user_settings = await repo.get(callback.from_user.id)
    user_settings.region = callback_data.value
    await repo.save(callback.from_user.id, user_settings)
    await cb_main_menu(callback, repo)


# --- Publication period ---------------------------------------------------------

@router.callback_query(SettingsCB.filter(F.action == "period"))
async def cb_period(callback: CallbackQuery) -> None:
    await callback.message.edit_text("🕒 За какой период искать треки?", reply_markup=period_kb()) # type: ignore
    await callback.answer()


@router.callback_query(SettingsCB.filter(F.action == "set_period"))
async def cb_set_period(callback: CallbackQuery, callback_data: SettingsCB, repo: SettingsRepository) -> None:
    user_settings = await repo.get(callback.from_user.id)
    user_settings.publish_time = PublishTime(callback_data.value)
    await repo.save(callback.from_user.id, user_settings)
    await cb_main_menu(callback, repo)


# --- Sorting ----------------------------------------------------------------

@router.callback_query(SettingsCB.filter(F.action == "sort"))
async def cb_sort(callback: CallbackQuery) -> None:
    await callback.message.edit_text("📊 Как сортировать результаты поиска?", reply_markup=sort_kb()) # type: ignore
    await callback.answer()


@router.callback_query(SettingsCB.filter(F.action == "set_sort"))
async def cb_set_sort(callback: CallbackQuery, callback_data: SettingsCB, repo: SettingsRepository) -> None:
    user_settings = await repo.get(callback.from_user.id)
    user_settings.sort_type = SortType(callback_data.value)
    await repo.save(callback.from_user.id, user_settings)
    await cb_main_menu(callback, repo)


# --- Number of tracks/videos per track ------------------------------------------

@router.callback_query(SettingsCB.filter(F.action == "count"))
async def cb_count(callback: CallbackQuery) -> None:
    await callback.message.edit_text( # type: ignore
        "🔢 Сколько уникальных треков присылать за один запуск /trends?", reply_markup=count_kb()
    )
    await callback.answer()


@router.callback_query(SettingsCB.filter(F.action == "set_count"))
async def cb_set_count(callback: CallbackQuery, callback_data: SettingsCB, repo: SettingsRepository) -> None:
    user_settings = await repo.get(callback.from_user.id)
    user_settings.tracks_count = int(callback_data.value)
    await repo.save(callback.from_user.id, user_settings)
    await cb_main_menu(callback, repo)


@router.callback_query(SettingsCB.filter(F.action == "videos"))
async def cb_videos(callback: CallbackQuery) -> None:
    await callback.message.edit_text( # type: ignore
        "🎬 Сколько исходных видео показывать под каждым треком?", reply_markup=videos_per_track_kb()
    )
    await callback.answer()


@router.callback_query(SettingsCB.filter(F.action == "set_videos"))
async def cb_set_videos(callback: CallbackQuery, callback_data: SettingsCB, repo: SettingsRepository) -> None:
    user_settings = await repo.get(callback.from_user.id)
    user_settings.videos_per_track = int(callback_data.value)
    await repo.save(callback.from_user.id, user_settings)
    await cb_main_menu(callback, repo)
